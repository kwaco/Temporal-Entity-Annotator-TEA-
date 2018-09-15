# This is based on https://github.com/flomlo/ntm_keras/blob/master/ntm.py
# which again is based on https://github.com/EderSantana/seya/blob/master/seya/layers/ntm.py
import numpy as np
import tensorflow as tf

from keras import initializers
from keras.layers.recurrent import Recurrent, GRU, LSTM, _time_distributed_dense
from keras.layers.core import Dense
from keras.initializers import RandomNormal, Orthogonal, Zeros, Constant
from keras import backend as K
from keras.engine.topology import InputSpec 
from keras.activations import get as get_activations
from keras.activations import softmax, tanh, sigmoid, hard_sigmoid, relu


class StatefulController(LSTM):
    def build(self, input_shape):
        print("lalala buid the StatefulController........")
        if isinstance(input_shape, list):
            input_shape = input_shape[0]

        batch_size = input_shape[0] if self.stateful else None
        self.input_dim = input_shape[2]
        self.input_spec[0] = InputSpec(shape=(batch_size, None, self.input_dim))

        self.states = [None, None]
        if self.stateful:
            self.reset_states()
            print(".............states reset in controller!........")

        self.kernel = self.add_weight(shape=(self.input_dim, self.units * 4),
                                      name='kernel',
                                      initializer=self.kernel_initializer,
                                      regularizer=self.kernel_regularizer,
                                      constraint=self.kernel_constraint)
        self.recurrent_kernel = self.add_weight(
            shape=(self.units, self.units * 4),
            name='recurrent_kernel',
            initializer=self.recurrent_initializer,
            regularizer=self.recurrent_regularizer,
            constraint=self.recurrent_constraint)

        if self.use_bias:
            if self.unit_forget_bias:
                def bias_initializer(shape, *args, **kwargs):
                    return K.concatenate([
                        self.bias_initializer((self.units,), *args, **kwargs),
                        initializers.Ones()((self.units,), *args, **kwargs),
                        self.bias_initializer((self.units * 2,), *args, **kwargs),
                    ])
            else:
                bias_initializer = self.bias_initializer
            self.bias = self.add_weight(shape=(self.units * 4,),
                                        name='bias',
                                        initializer=bias_initializer,
                                        regularizer=self.bias_regularizer,
                                        constraint=self.bias_constraint)
        else:
            self.bias = None

        self.kernel_i = self.kernel[:, :self.units]
        self.kernel_f = self.kernel[:, self.units: self.units * 2]
        self.kernel_c = self.kernel[:, self.units * 2: self.units * 3]
        self.kernel_o = self.kernel[:, self.units * 3:]

        self.recurrent_kernel_i = self.recurrent_kernel[:, :self.units]
        self.recurrent_kernel_f = self.recurrent_kernel[:, self.units: self.units * 2]
        self.recurrent_kernel_c = self.recurrent_kernel[:, self.units * 2: self.units * 3]
        self.recurrent_kernel_o = self.recurrent_kernel[:, self.units * 3:]

        if self.use_bias:
            self.bias_i = self.bias[:self.units]
            self.bias_f = self.bias[self.units: self.units * 2]
            self.bias_c = self.bias[self.units * 2: self.units * 3]
            self.bias_o = self.bias[self.units * 3:]
        else:
            self.bias_i = None
            self.bias_f = None
            self.bias_c = None
            self.bias_o = None
        self.built = True


def _circulant(leng, n_shifts):
    # This is more or less the only code still left from the original author,
    # EderSantan @ Github.
    # My implementation would probably just be worse.
    # Below his original comment:
 
    """
    I confess, I'm actually proud of this hack. I hope you enjoy!
    This will generate a tensor with `n_shifts` of rotated versions the
    identity matrix. When this tensor is multiplied by a vector
    the result are `n_shifts` shifted versions of that vector. Since
    everything is done with inner products, everything is differentiable.

    Paramters:
    ----------
    leng: int > 0, number of memory locations
    n_shifts: int > 0, number of allowed shifts (if 1, no shift)

    Returns:
    --------
    shift operation, a tensor with dimensions (n_shifts, leng, leng)
    """
    eye = np.eye(leng)
    shifts = range(n_shifts//2, -n_shifts//2, -1)
    C = np.asarray([np.roll(eye, s, axis=1) for s in shifts])
    return K.variable(C.astype(K.floatx()))


def _renorm(x):
    return x / (K.sum(x, axis=1, keepdims=True))


def _cosine_distance(M, k):
    # this is equation (6), or as I like to call it: The NaN factory.
    nk = K.l2_normalize(k, axis=-1)
    nM = K.l2_normalize(M, axis=None)
    cosine_distance = K.batch_dot(nM, nk)
    return cosine_distance

def _controller_read_head_emitting_dim(m_depth, shift_range):
    # For calculating the controller output dimension, we need the output_dim of the whole layer
    # (which is only passed during building) plus all the stuff we need to interact with the memory,
    # calculated here:
    #
    # For every read head the addressing data (for details, see figure 2):
    #       key_vector (m_depth) 
    #       beta (1)
    #       g (1)
    #       shift_vector (shift_range)
    #       gamma (1)
    return (m_depth + 1 + 1 + shift_range + 1)

def _controller_write_head_emitting_dim(m_depth, shift_range):
    controller_read_head_emitting_dim = _controller_read_head_emitting_dim(m_depth, shift_range)
    # But what do for write heads? The adressing_data_dim is the same, but we emit additionally:
    #       erase_vector (m_depth)
    #       add_vector (m_depth)
    return controller_read_head_emitting_dim + 2*m_depth

def controller_input_output_shape(input_dim, output_dim, m_depth, n_slots, shift_range, read_heads, write_heads):
    controller_read_head_emitting_dim = _controller_read_head_emitting_dim(m_depth, shift_range)
    controller_write_head_emitting_dim = _controller_write_head_emitting_dim(m_depth, shift_range)

    # The controller output size consists of 
    #       the regular output dim
    # plus, for every read and write head the respective dims times the number of heads.
    controller_output_dim = (output_dim + 
            read_heads * controller_read_head_emitting_dim + 
            write_heads * controller_write_head_emitting_dim)
    # For the input shape of the controller the formula is a bit easier:
    #       the regular input_dim 
    # plus, for every read head:
    #       read_vector (m_depth).
    # So that results in:
    controller_input_dim = input_dim + read_heads * m_depth

    return controller_input_dim, controller_output_dim


class NeuralTuringMachine(Recurrent):
    """ Neural Turing Machines

    Non obvious parameter:
    ----------------------
    shift_range: int, number of available shifts, ex. if 3, avilable shifts are
                 (-1, 0, 1)
    n_slots: Memory width, defined in 3.1 as N
    m_depth: Memory depth at each location, defined in 3.1 as M
    controller_model: A keras model with required restrictions to be used as a controller.
                        The requirements are appropriate shape, linear activation and stateful=True if recurrent.
                        Default: One dense layer.
    activation: This is the activation applied to the layer output.
                        It can be either a Keras activation or a string like "tanh", "sigmoid", "linear" etc.
                        Default is linear.

    Known issues:
    -------------
    Currently batch_input_size is necessary. Or not? Im not even sure :(

    """
    def __init__(self, units, 
                        n_slots=50,
                        m_depth=20,
                        shift_range=3,
                        controller_model=None,
                        read_heads=1,
                        write_heads=1,
                        activation='sigmoid',
                        batch_size=1,
                        stateful=False,
                        **kwargs):
        self.output_dim = units
        self.units = units
        self.n_slots = n_slots
        self.m_depth = m_depth
        self.shift_range = shift_range
        self.controller = controller_model
        self.activation = get_activations(activation)
        self.read_heads = read_heads
        self.write_heads = write_heads
        self.batch_size = batch_size
        self.controller_states = None

        if self.controller is not None and self.controller.stateful:
            self.controller_with_state = True
        else:
            self.controller_with_state = False


        self.controller_read_head_emitting_dim = _controller_read_head_emitting_dim(m_depth, shift_range)
        self.controller_write_head_emitting_dim = _controller_write_head_emitting_dim(m_depth, shift_range)

        super(NeuralTuringMachine, self).__init__(**kwargs)

    def build(self, input_shape):
        batch_size, input_length, self.input_dim = input_shape
        self.input_spec = InputSpec(shape=input_shape)

        self.controller_input_dim, self.controller_output_dim = controller_input_output_shape(
                self.input_dim, self.units, self.m_depth, self.n_slots, self.shift_range, self.read_heads,
                self.write_heads)
            
        # Now that we've calculated the shape of the controller, we have add it to the layer/model.
        if self.controller is None:
            self.controller = Dense(
                name = "controller",
                activation = 'linear',
                bias_initializer = 'zeros',
                units = self.controller_output_dim,
                input_shape = (batch_size, input_length, self.controller_input_dim))
            self.controller.build(input_shape=(batch_size, input_length, self.controller_input_dim))
            self.controller_with_state = False


        # This is a fixed shift matrix
        self.C = _circulant(self.n_slots, self.shift_range)

        self.trainable_weights = self.controller.trainable_weights

        # We need to declare the number of states we want to carry around.
        # In our case the dimension seems to be 6 (LSTM) or 5 (GRU) or 4 (FF),
        # see self.get_initial_states, those respond to:
        # [old_ntm_output] + [init_M, init_wr, init_ww] +  [init_h] (LSMT and GRU) + [(init_c] (LSTM only))
        # old_ntm_output does not make sense in our world, but is required by the definition of the step function we
        # intend to use.
        # WARNING: What self.state_spec does is only poorly understood,
        # I only copied it from keras/recurrent.py.
        self.states = [None, None, None, None]
        self.state_spec = [InputSpec(shape=(self.batch_size, self.output_dim)),                            # old_ntm_output
                            InputSpec(shape=(self.batch_size, self.n_slots, self.m_depth)),                # Memory
                            InputSpec(shape=(self.batch_size, self.read_heads, self.n_slots)),   # weights_read
                            InputSpec(shape=(self.batch_size, self.write_heads, self.n_slots))]  # weights_write

        super(NeuralTuringMachine, self).build(input_shape)

    # def call(self, inputs, mask=None, training=None, initial_state=None):
    #     pass

    def get_initial_state(self, X):
        #if not self.stateful:
        #    self.controller.reset_states()

        init_old_ntm_output = K.ones((self.batch_size, self.output_dim), name="init_old_ntm_output")*0.001
        init_M = K.ones((self.batch_size, self.n_slots , self.m_depth), name='main_memory')*0.001
        init_wr = np.zeros((self.batch_size, self.read_heads, self.n_slots))
        init_wr[:,:,0] = 1  # bias term
        init_wr = K.variable(init_wr, name="init_weights_read")
        init_ww = np.zeros((self.batch_size, self.write_heads, self.n_slots))
        init_ww[:,:,0] = 1  # bias term
        init_ww = K.variable(init_ww, name="init_weights_write")

        return [init_old_ntm_output, init_M, init_wr, init_ww]

    # See chapter 3.1
    def _read_from_memory(self, weights, M):
        # see equation (2)
        # print ("M, read from memory return", M, K.sum((weights[:, :, None] * M), axis=1))
        return K.sum((weights[:, :, None] * M),axis=1)  # (batch_size, read_heads, m_depth)

    # See chapter 3.2
    def _write_to_memory_erase(self, M, w, e):
        # see equation (3)
        M_tilda = M * (1 - w[:, :, None]*e[:, None, :])
        return M_tilda

    def _write_to_memory_add(self, M_tilda, w, a):
        # see equation (4)
        M_out = M_tilda + w[:, :, None]*a[:, None, :]
        return M_out

    # This is the chain described in Figure 2, or in further detail by
    # Chapter 3.3.1 (content based) and Chapter 3.3.2 (location based)
    # C is our convolution function precomputed above.
    def _get_weight_vector(self, M, w_tm1, k, beta, g, s, gamma):
#        M = tf.Print(M, [M, w_tm1, k], message='get weights beg1: ')
#        M = tf.Print(M, [beta, g, s, gamma], message='get weights beg2: ')
        # Content adressing, see Chapter 3.3.1:
        num = beta * _cosine_distance(M, k)
        w_c  = K.softmax(num) # It turns out that equation (5) is just softmax.
        # Location adressing, see Chapter 3.3.2:
        # Equation 7:
        w_g = (g * w_c) + (1-g) * w_tm1
        # C_s is the circular convolution
        #C_w = K.sum((self.C[None, :, :, :] * w_g[:, None, None, :]),axis=3)
        # Equation 8:
        # TODO: Explain
        C_s = K.sum(K.repeat_elements(self.C[None, :, :, :], self.batch_size, axis=0) * s[:,:,None,None], axis=1)
        w_tilda = K.batch_dot(C_s, w_g)
        # Equation 9:
        w_out = _renorm(w_tilda ** gamma)

        return w_out

    def _run_controller(self, inputs, read_vector): # only one instance of input here?
        # print("inpusts, read_vector", inputs, read_vector)
        controller_input = K.concatenate([inputs, read_vector])  # inputs:(batch_size, input_dim), read_vector: (1, readvec_dim)
        if self.controller_with_state or len(self.controller.input_shape) == 3:
            # print('controller_input before', controller_input)  # should be (1, input_size)
            controller_input = controller_input[:,None,:] # now shape changed to (1, 1, input_size)) # pseudo time step 1
            # print('controller_input', controller_input)
            controller_output_states = self.controller(controller_input, initial_state=self.controller_states) # call with states
            # print('controller_output_states', controller_output_states)
            controller_output = controller_output_states[0]  # first output of controller (RNN)
            self.controller_states = controller_output_states[1:]

            if self.controller.output_shape == 3:
                controller_output = controller_output[:,0,:] # first output of the list (should be one-element list anyway)
        else:
            controller_output = self.controller(controller_input)

        return controller_output

    def _split_and_apply_activations(self, controller_output):
        """ This takes the controller output, splits it in ntm_output, read and wright adressing data.
            It returns a triple of ntm_output, controller_instructions_read, controller_instructions_write.
            ntm_output is a tensor, controller_instructions_read and controller_instructions_write are lists containing
            the adressing instruction (k, beta, g, shift, gamma) and in case of write also the writing constructions,
            consisting of an erase and an add vector. 

            As it is necesseary for stable results,
            k and add_vector is activated via tanh, erase_vector via sigmoid (this is critical!),
            shift via softmax,
            gamma is sigmoided, inversed and clipped (probably not ideal)
            g is sigmoided,
            beta is relu. the higher the value is, the more attention paid to matching targets
            """
        
        # splitting
        ntm_output, controller_instructions_read, controller_instructions_write = tf.split(
                    controller_output,
                    np.asarray([self.output_dim,
                                self.read_heads * self.controller_read_head_emitting_dim,
                                self.write_heads * self.controller_write_head_emitting_dim]),
                    axis=1)

        controller_instructions_read = tf.split(controller_instructions_read, self.read_heads, axis=1)
        controller_instructions_write = tf.split(controller_instructions_write, self.write_heads, axis=1)

        controller_instructions_read = [
                tf.split(single_head_data, np.asarray([self.m_depth, 1, 1, 3, 1]), axis=1) for 
                single_head_data in controller_instructions_read]
        
        controller_instructions_write = [
                tf.split(single_head_data, np.asarray([self.m_depth, 1, 1, 3, 1, self.m_depth, self.m_depth]), axis=1) for 
                single_head_data in controller_instructions_write]
        
        #activation
        ntm_output = self.activation(ntm_output)
        # controller_instructions_read = [(tanh(k), hard_sigmoid(beta)+0.5, sigmoid(g), softmax(shift), 1 + 9*sigmoid(gamma)) for
        #         (k, beta, g, shift, gamma) in controller_instructions_read]
        # controller_instructions_write = [
        #         (tanh(k), hard_sigmoid(beta)+0.5, sigmoid(g), softmax(shift), 1 + 9*sigmoid(gamma), hard_sigmoid(erase_vector), tanh(add_vector))  for
        #         (k, beta, g, shift, gamma, erase_vector, add_vector) in controller_instructions_write]
        controller_instructions_read = [
            (tanh(k), hard_sigmoid(beta)+5.0, sigmoid(g), softmax(shift), 10.0) for
            (k, beta, g, shift, gamma) in controller_instructions_read]

        controller_instructions_write = [
            (tanh(k), hard_sigmoid(beta)+5.0, sigmoid(g), softmax(shift), 10.0,
             hard_sigmoid(erase_vector), tanh(add_vector)) for
            (k, beta, g, shift, gamma, erase_vector, add_vector) in controller_instructions_write]
       
        return (ntm_output, controller_instructions_read, controller_instructions_write)
        


    # @property
    # def output_shape(self):
    #     input_shape = self.input_shape
    #     if self.return_sequences:
    #         return input_shape[0], input_shape[1], self.output_dim
    #     else:
    #         return input_shape[0], self.output_dim


    def step(self, layer_input, states):
        # As a step function MUST return its regular output as the first element in the list of states,
        # we have _ here.
        # print("layer_input", layer_input)
        # print("states", states)
        _, M, weights_read_tm1, weights_write_tm1 = states[:4]  # the first dimension of each output is always 1.
                                                                #  M:(1,128,20)

        # reshaping (TODO: figure out how save n-dimensional state) 
        weights_read_tm1 = K.reshape(weights_read_tm1,
                (self.batch_size, self.read_heads, self.n_slots))  # is it necessary?
        weights_write_tm1 = K.reshape(weights_write_tm1, 
                (self.batch_size, self.write_heads, self.n_slots))

        # We have the old memory M, and a read weighting w_read_tm1 calculated in the last
        # step. This is enough to calculate the read_vector we feed into the controller:
        memory_read_input = K.concatenate([self._read_from_memory(weights_read_tm1[:,i], M) for
                i in range(self.read_heads)])

        # Now feed the controller and let it run a single step, implemented by calling the step function directly,
        # which we have to provide with the actual input from outside, the information we've read an the states which
        # are relevant to the controller.
        controller_output = self._run_controller(layer_input, memory_read_input)

        # We take the big chunk of unactivated controller output and subdivide it into actual output, reading and
        # writing instructions. Also specific activions for each parameter are applied.
        ntm_output, controller_instructions_read, controller_instructions_write = \
                self._split_and_apply_activations(controller_output)


        # Now we want to write to the memory for each head. We have to be carefull about concurrency, otherwise there is
        # a chance the write heads will interact with each other in unintended ways!
        # We first calculate all the weights, then perform all the erasing and only after that the adding is done.
        # addressing:
        weights_write = []
        for i in range(self.write_heads):
            write_head = controller_instructions_write[i]
            old_weight_vector = weights_write_tm1[:,i]
            weight_vector = self._get_weight_vector(M, old_weight_vector, *tuple(write_head[:5]))
            weights_write.append(weight_vector)
        # erasing:
        for i in range(self.write_heads):
            M = self._write_to_memory_erase(M, weights_write[i], controller_instructions_write[i][5])
        # adding:
        for i in range(self.write_heads):
            M = self._write_to_memory_add(M, weights_write[i], controller_instructions_write[i][6])

        # Only one thing left until this step is complete: Calculate the read weights we save in the state and use next
        # round:
        # As reading is side-effect-free, we dont have to worry about concurrency.
        weights_read = []
        for i in range(self.read_heads):
            read_head = controller_instructions_read[i]
            old_weight_vector = weights_read_tm1[:,i]
            weight_vector = self._get_weight_vector(M, old_weight_vector, *read_head)
            weights_read.append(weight_vector)

        # M = tf.Print(M, [K.mean(M), K.max(M), K.min(M)], message="Memory overview")
        # Now lets pack up the state in a list and call it a day.
        return ntm_output, [ntm_output, M, K.stack(weights_read, axis=1), K.stack(weights_write, axis=1)]

    def get_config(self):
        config = {'units' : self.output_dim,
        'n_slots' : self.n_slots,
        'm_depth' : self.m_depth,
        'shift_range' : self.shift_range,
        'controller_model' : self.controller,
        'read_heads' : self.read_heads,
        'write_heads' : self.write_heads,
        'activation' : self.activation,
        'batch_size' : self.batch_size,
        'stateful' : self.stateful}

        base_config = super(NeuralTuringMachine, self).get_config()

        return dict(list(base_config.items()) + list(config.items()))

    @classmethod
    def from_config(cls, config):
        return cls(**config)

