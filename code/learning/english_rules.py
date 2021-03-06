"""The rules within english_rules.txt come from the original authors of this pape
"""
import os
import re
import sys

from code.notes.utilities.pre_processing import morpho_pro

# TODO: i don't check tests on the negative case very exhaustively. need to add more negative cases.

TEA_HOME_DIR = os.path.join(*([os.path.dirname(os.path.abspath(__file__))] + [".."]*2))

# be/indic/pres + _v_/gerund/pres = tense=PRESENT, aspect=PROGRESSIVE
_ACTIVE_VOICE_PRESENT_PROGRESSIVE_RE = "^be\+.*\+indic\+pres||^.+\+v\+.*gerund\+pres"
# have/indic/pres + be/part/past + _v_/gerund/pres = tense=PRESENT, aspect=PERFECTIVE_PROGRESSIVE
_ACTIVE_VOICE_PRESENT_PERFECTIVE_PROGRESSIVE_RE = "^have\+.*\+indic\+pres||^be\+.*\+part\+past||^.+\+v\+.*gerund\+pres"
 # have/indic/pres + _v_/part/past = tense=PRESENT, aspect=PERFECTIVE
_ACTIVE_VOICE_PRESENT_PERFECTIVE_RE = "^have\+.*\+indic\+pres||.+\+v\+.*part\+past"

# be/indic/past + _v_/gerund/pres = tense=PAST, aspect=PROGRESSIVE
_ACTIVE_VOICE_PAST_PROGRESSIVE_RE = "^be\+.*\+indic\+past||^.+\+v\+.*gerund\+pres"
# have/indic/past + _v_/part/past = tense=PAST, aspect=PERFECTIVE
_ACTIVE_VOICE_PAST_PERFECTIVE_RE =  "^have\+.*\+indic\+past||^.+\+v\+.*part\+past"
# have/indic/past + be/part/past + _v_/gerund/pres = tense=PAST, aspect=PERFECTIVE_PROGRESSIVE
_ACTIVE_VOICE_PAST_PERFECTIVE_PROGRESSIVE_RE = "^have\+.*\+indic\+past||^be\+.*\+part\+past||^.+\+v\+.*gerund\+pres"

# will/indic/pres + _v_/infin/pres = tense=FUTURE, aspect=NONE
_ACTIVE_VOICE_FUTURE_NONE_A_RE = "^will\+.*\+indic\+pres||^.+\+v\+.*infin\+pres"
# will/indic/pres + _v_/indic/pres = tense=FUTURE, aspect=NONE
_ACTIVE_VOICE_FUTURE_NONE_B_RE = "^will\+.*\+indic\+pres||^.+\+v\+.*indic\+pres"
# be/indic/pres + go/gerund/pres + to + _v_/infin/pres = tense=FUTURE, aspect=NONE
_ACTIVE_VOICE_FUTURE_NONE_C_RE = "^be\+.*\+indic\+pres||^go\+.*\+gerund\+pres||^to\+.*||^.+\+v\+.*infin\+pres"
# will/indic/pres + be/infin/pres + _v_/gerund/pres = tense=FUTURE, aspect=PROGRESSIVE
_ACTIVE_VOICE_FUTURE_PROGRESSIVE_A_RE = "^will\+.*\+indic\+pres||^be\+.*\+infin\+pres||^.+\+v\+.*gerund\+pres"
# be/indic/pres + go/gerund/pres + to + be/infin/pred + _v_/infin/pres = tense=FUTURE, aspect=PROGRESSIVE
_ACTIVE_VOICE_FUTURE_PROGRESSIVE_B_RE = "^be\+.*\+indic\+pres||^go\+.*\+gerund\+pres||^to\+.*||^be\+.*infin\+pres||^.+\+v\+.*gerund\+pres"
# will/indic/pres + have/infin/pres + _v_/part/past = tense=FUTURE, aspect=PERFECTIVE
_ACTIVE_VOICE_FUTURE_PERFECTIVE_RE = "^will\+.*\+indic\+pres||^have\+.*\+infin\+pres||^.+\+v\+.*part\+past"
# will/indic/pres + have/infin/pres + be/part/past +  _v_/gerund/pres = tense=FUTURE, aspect=PERFECTIVE_PROGRESSIVE
_ACTIVE_VOICE_FUTURE_PERFECTIVE_PROGRESSIVE_RE = "^will\+.*\+indic\+pres||^have\+.*\+infin\+pres||^be\+.*part\+past||^.+\+v\+.*gerund\+pres"


# be/indic/pres + _v_/part/past = tense=PRESENT, aspect=NONE
_PASSIVE_VOICE_PRESENT_RE = "^be\+.*\+indic\+pres||^.+\+v\+.*part\+past"
# be/indic/pres + be/gerund/pres + _v_/part/past = tense=PRESENT, aspect=PROGRESSIVE
_PASSIVE_VOICE_PRESENT_PROGRESSIVE_RE = "^be\+.*\+indic\+pres||^be\+.*\+gerund\+pres||^.+\+v\+.*part\+past"
# have/indic/pres + be/part/past + _v_/part/past = tense=PRESENT, aspect=PERFECTIVE
_PASSIVE_VOICE_PRESENT_PERFECTIVE_RE = "^have\+.*\+indic\+pres||^be\+.*\+part\+past||^.+\+v\+.*part\+past"
# be/indic/past + _v_/part/past = tense=PAST, aspect=NONE
_PASSIVE_VOICE_PAST_RE = "^be\+.*\+indic\+past||^.+\+v\+.*part\+past"
# be/indic/past + be/gerund/pres + _v_/part/past = tense=PAST, aspect=PROGRESSIVE
_PASSIVE_VOICE_PAST_PROGRESSIVE_RE = "^be\+.*\+indic\+past||^be\+.*\+gerund\+pres|^.+\+v\+.*part\+past"
# have/indic/past + be/part/past + _v_/part/past = tense=PAST, aspect=PERFECTIVE
_PASSIVE_VOICE_PAST_PERFECTIVE_RE = "^have\+.*\+indic\+past||^be\+.*\+part\+past||^.+\+v\+.*part\+past"
# will/indic/pres + be/infin/pres + _v_/part/past = tense=FUTURE, aspect=NONE
_PASSIVE_VOICE_FUTURE_A_RE = "^will\+.*\+indic\+pres||^be\+.*\+infin\+pres||^.+\+v\+.*part\+past"
# be/indic/pres + go/gerund/pres + to + be/infin/pres + _v_/part/past = tense=FUTURE, aspect=NONE
_PASSIVE_VOICE_FUTURE_B_RE = "^be\+.*\+indic\+pres||^go\+.*\+gerund\+pres||^to\+.*||^be\+.*infin\+pres||^.+\+v\+.*part\+past"
# will/indic/pres + have/infin/pres + be/part/past + _v_/part/past = tense=FUTURE, aspect=PERFECTIVE
_PASSIVE_VOICE_FUTURE_PERFECTIVE_RE = "^will\+.*\+indic\+pres||^have\+.*\+infin\+pres||^be\+.*part\+past||^.+\+v\+.*part\+past"


# have/indic/pres + to + _v_/infin/pres = tense=PRESENT, aspect=NONE
_MODAL_PRESENT_RE = "^have\+.*\+indic\+pres||^to\+.*||^.+\+v\+.*infin\+pres"
# have/indic/pres + to + be/infin/pres + _v_/gerund/pres = tense=PRESENT, aspect=PROGRESSIVE
_MODAL_PRESENT_PROGRESSIVE_RE = "^have\+.*\+indic\+pres||^to.*||^be\+.*infin\+pres||^.+\+v\+.*gerund\+pres"
# have/indic/pres + to + have/infin/pres + _v_/part/past = tense=PRESENT, aspect=PERFECTIVE
_MODAL_PRESENT_PERFECTIVE_RE = "^have\+.*\+indic\+pres||^to.*||^have\+.*infin\+pres||^.+\+v\+.*part\+past"
# have/indic/pres + to + have/infin/pres + be/part/past + _v_/gerund/pres = tense=PRESENT, aspect=PERFECTIVE_PROGRESSIVE
_MODAL_PRESENT_PERFECTIVE_PROGRESSIVE_RE = "^have\+.*\+indic\+pres||^to.*||^have\+.*infin\+pres||^be\+v\+.*part\+past||^.+\+v\+.*gerund\+pres"
# have/indic/past + to + _v_/infin/pres = tense=PAST, aspect=NONE
_MODAL_PAST_NONE_A_RE = "^have\+.*\+indic\+past||^to.*||^.+\+v\+.*infin\+pres"
# have/indic/past + to + be/infin/pres + _v_/gerund/pres = tense=PAST, aspect=PROGRESSIVE
_MODAL_PAST_PROGRESSIVE_RE = "^have\+.*\+indic\+past||^to.*||^be\+.*infin\+pres||^.+\+v\+.*gerund\+pres"
# will/indic/pres + have/infin/pres + to + _v_/infin/pres = tense=FUTURE, aspect=NONE
_MODAL_FUTURE_RE = "^will\+.*\+indic\+pres||^have\+.*infin\+pres||^to.*||^.+\+v\+.*infin\+pres"
# will/indic/pres + have/infin/pres + to + be/infin/pres + _v_/gerund/pres = tense=FUTURE, aspect=PROGRESSIVE
_MODAL_FUTURE_PROGRESSIVE_RE = "^will\+.*indic\+pres||^have\+.*infin\+pres||^to.*||^be\+.*infin\+pres||^.+\+v\+.*gerund\+pres"
# (must|should|may|might|can|could|would) + _v_/infin/pres = tense=NONE, aspect=NONE
_MODAL_NONE_NONE_RE = "^(must|should|may|might|can|could|would)\+.*||^.+\+v\+.*infin\+pres"
# (must|should|may|might|can|could|would) + be/infin/pres + _v_/gerund/pres = tense=NONE, aspect=PROGRESSIVE
_MODAL_NONE_PROGRESSIVE_RE = "^(must|should|may|might|can|could|would)\+.*||^be\+.*infin\+pres||^.+\+v\+.*gerund\+pres"
# (must|should|may|might|can|could|would) + have/infin/pres +_v_/part/past = tense=NONE, aspect=PERFECTIVE
_MODAL_NONE_PERFECTIVE_RE = "^(must|should|may|might|can|could|would)\+.*||^have\+.*infin\+pres||^.+\+v\+.*part\+past"
# (must|should|may|might|can|could|would) + have/infin/pres + been/part/past +_v_/gerund/pres = tense=NONE, aspect=PERFECTIVE_PROGRESSIVE
_MODAL_NONE_PERFECTIVE_PROGRESSIVE = "^(must|should|may|might|can|could|would)\+.*||^have\+.*infin\+pres||^be\+.*part\+past||^.+\+v\+.*gerund\+pres"
# (must|should|may|might|can|could|would) + be/infin/pres + _v_/part/past = tense=PAST, aspect=NONE
_MODAL_PAST_NONE_B_RE = "^(must|should|may|might|can|could|would)\+.*||^be\+.*infin\+pres||^.+\+v\+.*part\+past"

# do/indic/past + _v_/infin/pres = tense=PAST, aspect=NONE
_DO_PAST_RE = "^do\+.*indic\+past||^.+\+v\+.*infin\+pres"
# do/indic/pres + _v_/infin/pres = tense=PRESENT, aspect=NONE
_DO_PRESENT_RE = "^do\+.*indic\+pres||^.+\+v\+.*infin\+pres"
# to + _v_/infin/pres = tense=INFINITIVE, aspect=NONE
_INFINITIVE_NONE_A_RE = "^to\+.*||^.+\+v\+.*infin\+pres"
# to + _v_/indic/pres = tense=INFINITIVE, aspect=NONE
_INFINITIVE_NONE_B_RE = "^to\+.*||^.+\+v\+.*indic\+pres"
# to + be/infin/pres + _v_/gerund/pres = tense=INFINITIVE, aspect=PROGRESSIVE
_INFITIVE_PROGRESSIVE_RE = "^to\+.*||^be\+.*\+infin\+pres||^.+\+v\+.*gerund\+pres"
# to + have/infin/pres + _v_/part/past = tense=INFINITIVE, aspect=PERFECTIVE
_INFINITIVE_PERFECTIVE_RE = "^to\+.*||^have\+.*\+infin\+pres||^.+\+v\+.*part\+past"
# to + have/infin/pres + be/part/past + _v_/gerund/pres = tense=INFINITIVE, aspect=PERFECTIVE_PROGRESSIVE
_INFINITIVE_PERFECTIVE_PROGRESSIVE_RE = "^to\+.*||^have\+.*\+infin\+pres||^be\+.*\+part\+past||^.+\+v\+.*gerund\+pres"

# _v_/gerund/pres = tense=PRESPART, aspect=NONE
_PRESPART_RE = "^.+\+v\+.*gerund\+pres"
# _v_/indic/pres = tense=PRESENT, aspect=NONE
_PRESENT_RE = "^.+\+v\+.*indic\+pres"
# _v_/indic/past = tense=PAST, aspect=NONE
_PAST_RE = "^.+\+v\+.*indic\+past"
# _v_/part/past = tense=PASTPART, aspect=NONE
_PASTPART_RE = "^.+\+v\+.*part\+past"

# be/part/past + _v_/gerund/pres = tense=NONE, aspect=PERFECTIVE_PROGRESSIVE
_TWO_PIECE_VP_NONE_PERFECTIVE_PROGRESSIVE_RE = "^be\+.*\+part\+past||^.+\+v\+.*gerund\+pres"
# be/part/past + _v_/part/past = tense=NONE, aspect=PERFECTIVE
_TWO_PIECE_VP_NONE_PERFECTIVE_RE = "^be\+.*\+part\+past||^.+\+v\+.*part\+past"

# _v_/gerund/pres = tense=PRESPART, aspect=NONE
_PRESPART_NONE_RE = "^.+\+v\+.*gerund\+pres"

# be/indic/pres + _a_ = tense=PRESENT, aspect=NONE
_ADJ_PRESENT_RE = "^be\+.*\+indic\+pres||^.*\+adj"
# be/indic/pres + be/gerund/pres + _a_ = tense=PRESENT, aspect=PROGRESSIVE
_ADJ_PRESENT_PROGRESSIVE_RE = "^be\+.*\+indic\+pres||^be\+.*\+gerund\+pres||^.*\+adj"
# have/indic/pres + be/part/past + _a_ = tense=PRESENT, aspect=PERFECTIVE
_ADJ_PRESENT_PERFECTIVE_RE = "^have\+.*\+indic\+pres||^be\+.*\+part\+past||^.*\+adj"
# be/indic/past + _a_ = tense=PAST, aspect=NONE
_ADJ_PAST_RE = "^be\+.*\+indic\+past||^.*\+adj"
# be/indic/past + be/gerund/pres + _a_ = tense=PAST, aspect=PROGRESSIVE
_ADJ_PAST_PROGRESSIVE_RE = "^be\+.*\+indic\+past||^be\+.*\+gerund\+pres||^.*\+adj"
# have/indic/past + be/part/past + _a_ = tense=PAST, aspect=PERFECTIVE
_ADJ_PAST_PERFECTIVE_RE = "^have\+.*\+indic\+past||^be\+.*\+part\+past||^.*\+adj"
# will/indic/pres + be/infin/pres + _a_ = tense=FUTURE, aspect=NONE
_ADJ_FUTURE_RE = "^will\+.*\+indic\+pres||^be\+.*\+infin\+pres||^.*\+adj"
# will/indic/pres + have/infin/pres + be/part/past + _a_ = tense=FUTURE, aspect=PERFECTIVE
_ADJ_FUTURE_PERFECTIVE_RE = "^will\+.*\+indic\+pres||have\+.*\+infin\+pres||^be\+.*\+part\+past||^.*\+adj"

# be/indic/pres + _n_ = tense=PRESENT, aspect=NONE
_NOUN_PRESENT_RE = "^be\+.*\+indic\+pres||^.*\+n(\+.*|\Z)"
# be/indic/pres + be/gerund/pres + _n_ = tense=PRESENT, aspect=PROGRESSIVE
_NOUN_PRESENT_PROGRESSIVE_RE = "^be\+.*\+indic\+pres||^be\+.*\+gerund\+pres||^.*\+n(\+.*|\Z)"
# have/indic/pres + be/part/past + _n_ = tense=PRESENT, aspect=PERFECTIVE
_NOUN_PRESENT_PERFECTIVE_RE = "^have\+.*\+indic\+past||^be\+.*\+part\+past||^.*\+n(\+.*|\Z)"
# be/indic/past + _n_ = tense=PAST, aspect=NONE
_NOUN_PAST_RE = "^be\+.*\+indic\+past||^.*\+n(\+.*|\Z)"
# be/indic/past + be/gerund/pres + _n_ = tense=PAST, aspect=PROGRESSIVE
_NOUN_PAST_PROGRESSIVE_RE = "^be\+.*\+indic\+past||^be\+.*\+gerund\+pres||^.*\+n(\+.*|\Z)"
# have/indic/past + be/part/past + _n_ = tense=PAST, aspect=PERFECTIVE
_NOUN_PAST_PERFECTIVE_RE = "^have\+.*\+indic\+past||^be\+.*\+part\+past||^.*\+n(\+.*|\Z)"
# will/indic/pres + be/infin/pres + _n_ = tense=FUTURE, aspect=NONE
_NOUN_FUTURE_RE = "^will\+.*\+indic\+pres||^be\+.*\+infin\+pres||^.*\+n(\+.*|\Z)"
# will/indic/pres + have/infin/pres + be/part/past + _n_ = tense=FUTURE, aspect=PERFECTIVE
_NOUN_FUTURE_PERFECTIVE_RE = "^will\+.*\+indic\+pres||^have\+.*\+indic\+pres||^be\+.*\+part\+past||^.*\+n(\+.*|\Z)"


# be/indic/pres + _p_ = tense=PRESENT, aspect=NONE
_PREP_PRESENT_RE = "^be\+.*\+indic\+pres||^.*\+prep(\+.*|\Z)"
# be/indic/pres + be/gerund/pres + _p_ = tense=PRESENT, aspect=PROGRESSIVE
_PREP_PRESENT_PROGRESSIVE_RE = "^be\+.*\+indic\+pres||^be\+.*\+gerund\+pres||^.*\+prep(\+.*|\Z)"
# have/indic/pres + be/part/past + _p_ = tense=PRESENT, aspect=PERFECTIVE
_PREP_PRESENT_PERFECTIVE_RE = "^have\+.*\+indic\+pres||^be\+.*\+part\+past||^.*\+prep(\+.*|\Z)"
# be/indic/past + _p_ = tense=PAST, aspect=NONE
_PREP_PAST = "^be\+.*\+indic\+past||^.*\+prep(\+.*|\Z)"
# be/indic/past + be/gerund/pres + _p_ = tense=PAST, aspect=PROGRESSIVE
_PREP_PAST_PROGRESSIVE_RE = "^be\+.*\+indic\+past||^be\+.*\+gerund\+pres||^.*\+prep(\+.*|\Z)"
# have/indic/past + be/part/past + _p_ = tense=PAST, aspect=PERFECTIVE
_PREP_PAST_PERFECTIVE_RE = "^have\+.*\+indic\+past||^be\+.*\+part\+past||^.*\+prep(\+.*|\Z)"
# will/indic/pres + be/infin/pres + _p_ = tense=FUTURE, aspect=NONE
_PREP_FUTURE_RE = "^will\+.*\+indic\+pres||^be\+.*\+infin\+pres||^.*\+prep(\+.*|\Z)"
# will/indic/pres + have/infin/pres + be/part/past + _p_ = tense=FUTURE, aspect=PERFECTIVE
_PREP_FUTURE_PERFECTIVE_RE = "^will\+.*\+indic\+pres||^have\+.*\+infin\+pres||^be\+.*\+part\+past||^.*\+prep(\+.*|\Z)"

_TENSE_ASPECT =  {

            # TODO: look at what the formatating is for TimeML
            _ACTIVE_VOICE_PRESENT_PROGRESSIVE_RE: {"tense":"PRESENT", "aspect":"PROGRESSIVE"},
            _ACTIVE_VOICE_PRESENT_PERFECTIVE_PROGRESSIVE_RE: {"tense":"PRESENT", "aspect":"PERFECTIVE_PROGRESSIVE"},
            _ACTIVE_VOICE_PRESENT_PERFECTIVE_RE: {"tense":"PRESENT", "aspect":"PERFECTIVE"},

            _ACTIVE_VOICE_PAST_PROGRESSIVE_RE: {"tense":"PAST", "aspect":"PROGRESSIVE"},
            _ACTIVE_VOICE_PAST_PERFECTIVE_RE: {"tense":"PAST", "aspect":"PERFECTIVE"},
            _ACTIVE_VOICE_PAST_PERFECTIVE_PROGRESSIVE_RE: {"tense":"PAST", "aspect":"PERFECTIVE_PROGRESSIVE"},

            _ACTIVE_VOICE_FUTURE_NONE_A_RE: {"tense":"FUTURE", "aspect":"NONE"},
            _ACTIVE_VOICE_FUTURE_NONE_B_RE: {"tense":"FUTURE", "aspect":"NONE"},
            _ACTIVE_VOICE_FUTURE_NONE_C_RE: {"tense":"FUTURE", "aspect":"NONE"},
            _ACTIVE_VOICE_FUTURE_PROGRESSIVE_A_RE: {"tense":"FUTURE", "aspect":"PROGRESSIVE"},
            _ACTIVE_VOICE_FUTURE_PROGRESSIVE_B_RE: {"tense":"FUTURE", "aspect":"PROGRESSIVE"},
            _ACTIVE_VOICE_FUTURE_PERFECTIVE_RE: {"tense":"FUTURE", "aspect":"PROGRESSIVE"},
            _ACTIVE_VOICE_FUTURE_PERFECTIVE_PROGRESSIVE_RE: {"tense":"FUTURE", "aspect":"PERFECTIVE_PROGRESSIVE"},

            _PASSIVE_VOICE_PRESENT_RE: {"tense":"PRESENT", "aspect":"NONE"},
            _PASSIVE_VOICE_PRESENT_PROGRESSIVE_RE: {"tense":"PRESENT", "aspect":"PROGRESSIVE"},
            _PASSIVE_VOICE_PRESENT_PERFECTIVE_RE: {"tense":"PRESENT", "aspect":"PERFECTIVE"},
            _PASSIVE_VOICE_PAST_RE: {"tense":"PAST", "aspect":"NONE"},
            _PASSIVE_VOICE_PAST_PROGRESSIVE_RE: {"tense":"PAST", "aspect":"PROGRESSIVE"},
            _PASSIVE_VOICE_PAST_PERFECTIVE_RE: {"tense":"PAST", "aspect":"PERFECTIVE"},
            _PASSIVE_VOICE_FUTURE_A_RE: {"tense":"FUTURE", "aspect":"NONE"},
            _PASSIVE_VOICE_FUTURE_B_RE: {"tense":"FUTURE", "aspect":"NONE"},
            _PASSIVE_VOICE_FUTURE_PERFECTIVE_RE: {"tense":"FUTURE", "aspect":"PERFECTIVE"},

            _MODAL_PRESENT_RE:{"tense":"PRESENT", "aspect":"NONE"},
            _MODAL_PRESENT_PROGRESSIVE_RE:{"tense":"PRESENT", "aspect":"PROGRESSIVE"},
            _MODAL_PRESENT_PERFECTIVE_RE: {"tense":"PRESENT", "aspect":"PERFECTIVE"},
            _MODAL_PRESENT_PERFECTIVE_PROGRESSIVE_RE:{"tense":"PRESENT", "aspect":"PERFECTIVE_PROGRESSIVE"},
            _MODAL_PAST_NONE_A_RE: {"tense":"PAST", "aspect":"NONE"},
            _MODAL_PAST_PROGRESSIVE_RE: {"tense":"PAST", "aspect":"PROGRESSIVE"},
            _MODAL_FUTURE_RE: {"tense":"FUTURE", "aspect":"NONE"},
            _MODAL_FUTURE_PROGRESSIVE_RE: {"tense":"FUTURE", "aspect":"PROGRESSIVE"},
            _MODAL_NONE_NONE_RE: {"tense":"NONE", "aspect":"NONE"},
            _MODAL_NONE_PROGRESSIVE_RE: {"tense":"NONE", "aspect":"PROGRESSIVE"},
            _MODAL_NONE_PERFECTIVE_RE: {"tense":"NONE", "aspect":"PERFECTIVE"},
            _MODAL_NONE_PERFECTIVE_PROGRESSIVE: {"tense":"NONE", "aspect":"PROGRESSIVE"},
            _MODAL_PAST_NONE_B_RE: {"tense":"PAST", "aspect":"NONE"},

            _DO_PAST_RE: {"tense":"PAST", "aspect":"NONE"},
            _DO_PRESENT_RE: {"tense":"PRESENT", "aspect":"NONE"},
            _INFINITIVE_NONE_A_RE: {"tense":"INFINITIVE", "aspect": "NONE"},
            _INFINITIVE_NONE_B_RE: {"tense":"INFINITIVE", "aspect":"NONE"},
            _INFITIVE_PROGRESSIVE_RE: {"tense":"INFINITIVE", "aspect":"PROGRESSIVE"},
            _INFINITIVE_PERFECTIVE_RE: {"tense":"INFINITIVE", "aspect":"PERFECTIVE"},
            _INFINITIVE_PERFECTIVE_PROGRESSIVE_RE: {"tense":"INFINITIVE", "aspect":"PERFECTIVE_PROGRESSIVE"},


            _PRESPART_RE: {"tense":"PRESPART", "aspect":"NONE"},
            _PRESENT_RE: {"tense":"PRESENT", "aspect":"NONE"},
            _PAST_RE: {"tense":"PAST", "aspect":"NONE"},
            _PASTPART_RE: {"tense":"PASTPART", "aspect":"NONE"},

            _TWO_PIECE_VP_NONE_PERFECTIVE_PROGRESSIVE_RE: {"tense":"NONE", "aspect":"PERFECTIVE_PROGRESSIVE"},
            _TWO_PIECE_VP_NONE_PERFECTIVE_RE: {"tense":"NONE", "aspect":"PERFECTIVE"},

            _PRESPART_NONE_RE: {"tense":"PRESPART", "aspect":"NONE"},

            _ADJ_PRESENT_RE: {"tense":"PRESENT", "aspect":"NONE"},
            _ADJ_PRESENT_PROGRESSIVE_RE: {"tense":"PRESENT", "aspect":"PROGRESSIVE"},
            _ADJ_PRESENT_PERFECTIVE_RE: {"tense":"PRESENT", "aspect":"PERFECTIVE"},
            _ADJ_PAST_RE: {"tense":"PAST", "aspect":"NONE"},
            _ADJ_PAST_PROGRESSIVE_RE: {"tense":"PAST", "aspect":"PROGRESSIVE"},
            _ADJ_PAST_PERFECTIVE_RE: {"tense":"PAST", "aspect":"PERFECTIVE"},
            _ADJ_FUTURE_RE: {"tense":"FUTURE", "aspect":"NONE"},
            _ADJ_FUTURE_PERFECTIVE_RE: {"tense":"FUTURE", "aspect":"PERFECTIVE"},


            _NOUN_PRESENT_RE: {"tense":"PRESENT", "aspect":"NONE"},
            _NOUN_PRESENT_PROGRESSIVE_RE: {"tense":"PRESENT", "aspect":"PROGRESSIVE"},
            _NOUN_PRESENT_PERFECTIVE_RE: {"tense":"PRESENT", "aspect":"PERFECTIVE"},
            _NOUN_PAST_RE: {"tense":"PAST", "aspect":"NONE"},
            _NOUN_PAST_PROGRESSIVE_RE: {"tense":"PAST", "aspect":"PROGRESSIVE"},
            _NOUN_PAST_PERFECTIVE_RE: {"tense":"PAST", "aspect":"PERFECTIVE"},
            _NOUN_FUTURE_RE: {"tense":"FUTURE", "aspect":"NONE"},
            _NOUN_FUTURE_PERFECTIVE_RE: {"tense":"FUTURE", "aspect":"PERFECTIVE"},


            _PREP_PRESENT_RE: {"tense":"PRESENT", "aspect":"NONE"},
            _PREP_PRESENT_PROGRESSIVE_RE: {"tense":"PRESENT", "aspect":"PROGRESSIVE"},
            _PREP_PRESENT_PERFECTIVE_RE: {"tense":"PRESENT", "aspect":"PERFECTIVE"},
            _PREP_PAST: {"tense":"PAST", "aspect":"NONE"},
            _PREP_PAST_PROGRESSIVE_RE: {"tense":"PAST", "aspect":"PROGRESSIVE"},
            _PREP_PAST_PERFECTIVE_RE: {"tense":"PAST", "aspect":"PERFECTIVE"},
            _PREP_FUTURE_RE: {"tense":"FUTURE", "aspect":"NONE"},
            _PREP_FUTURE_PERFECTIVE_RE: {"tense":"FUTURE", "aspect":"PERFECTIVE"},

          }

_MAX_ARG_LEN = 0

_NARG_TENSE_ASPECT = {}

# group each rule by number of len of token input
for rule in _TENSE_ASPECT.keys():
    arg_len = len(rule.split("||"))
    if arg_len > _MAX_ARG_LEN:
        _MAX_ARG_LEN = arg_len

    if arg_len in _NARG_TENSE_ASPECT:
        _NARG_TENSE_ASPECT[arg_len][rule] = _TENSE_ASPECT[rule]
    else:
        _NARG_TENSE_ASPECT[arg_len] = {rule:_TENSE_ASPECT[rule]}


_RULE_NAMES = {

                _ACTIVE_VOICE_PRESENT_PROGRESSIVE_RE: "ACTIVE VOICE: PRESENT PROGRESSIVE",
                _ACTIVE_VOICE_PRESENT_PERFECTIVE_PROGRESSIVE_RE: "ACTIVE VOICE: PRESENT PERFECTIVE-PROGRESSIVE",
                _ACTIVE_VOICE_PRESENT_PERFECTIVE_RE: "ACTIVE VOICE: PRESENT PERFECTIVE",

                _ACTIVE_VOICE_PAST_PROGRESSIVE_RE: "ACTIVE VOICE: PAST PROGRESSIVE",
                _ACTIVE_VOICE_PAST_PERFECTIVE_RE: "ACTIVE VOICE: PAST PERFECTIVE",
                _ACTIVE_VOICE_PAST_PERFECTIVE_PROGRESSIVE_RE: "ACTIVE VOICE: PERFECTIVE PROGRESSIVE",

                _ACTIVE_VOICE_FUTURE_NONE_A_RE: "ACTIVE VOICE: FUTURE NONE",
                _ACTIVE_VOICE_FUTURE_NONE_B_RE: "ACTIVE VOICE: FUTURE NONE",
                _ACTIVE_VOICE_FUTURE_NONE_C_RE: "ACTIVE VOICE: FUTURE NONE",
                _ACTIVE_VOICE_FUTURE_PROGRESSIVE_A_RE: "ACTIVE VOICE: FUTURE PROGRESSIVE",
                _ACTIVE_VOICE_FUTURE_PROGRESSIVE_B_RE: "ACTIVE VOICE: FUTURE PROGRESSIVE",
                _ACTIVE_VOICE_FUTURE_PERFECTIVE_RE: "ACTIVE VOICE: FUTURE PERFECTIVE",
                _ACTIVE_VOICE_FUTURE_PERFECTIVE_PROGRESSIVE_RE: "ACTIVE VOICE: PERFECTIVE PROGRESSIVE",

                _PASSIVE_VOICE_PRESENT_RE: "PASSIVE VOICE: PRESENT",
                _PASSIVE_VOICE_PRESENT_PROGRESSIVE_RE: "PASSIVE VOICE: PRESENT PROGRESSIVE",
                _PASSIVE_VOICE_PRESENT_PERFECTIVE_RE: "PASSIVE VOICE: PRESENT PERFECTIVE",
                _PASSIVE_VOICE_PAST_RE: "PASSIVE VOICE: PAS",
                _PASSIVE_VOICE_PAST_PROGRESSIVE_RE: "PASSIVE VOICE: PAST PROGRESSIVE",
                _PASSIVE_VOICE_PAST_PERFECTIVE_RE: "PASSIVE VOICE: PAST PERFECTIVE",
                _PASSIVE_VOICE_FUTURE_A_RE: "PASSIVE VOICE: FUTURE A",
                _PASSIVE_VOICE_FUTURE_B_RE: "PASSIVE VOICEL FUTURE B",
                _PASSIVE_VOICE_FUTURE_PERFECTIVE_RE: "PASSIVE VOICE: FUTURE PERFECTIVE",

                _MODAL_PRESENT_RE: "MODAL: PRESENT",
                _MODAL_PRESENT_PROGRESSIVE_RE: "MODAL: PRESENT PROGRESSIVE",
                _MODAL_PRESENT_PERFECTIVE_RE: "MODAL: PRESENT PERFECTIVE",
                _MODAL_PRESENT_PERFECTIVE_PROGRESSIVE_RE: "MODAL: PRESENTER PERFECTIVE-PROGRESSIVE",
                _MODAL_PAST_NONE_A_RE: "MODAL: PAST",
                _MODAL_PAST_PROGRESSIVE_RE: "MODAL: PAST PROGRESSIVE",
                _MODAL_FUTURE_RE: "MODAL: FUTURE",
                _MODAL_FUTURE_PROGRESSIVE_RE: "MODAL: FUTURE PROGRESSIVE",
                _MODAL_NONE_NONE_RE: "MODAL: NONE NONE",
                _MODAL_NONE_PROGRESSIVE_RE: "MODAL: NONE PROGRESSIVE",
                _MODAL_NONE_PERFECTIVE_RE: "MODAL: NONE PERFECTIVE",
                _MODAL_NONE_PERFECTIVE_PROGRESSIVE: "MODAL: PERFECTIVE PROGRESSIVE",
                _MODAL_PAST_NONE_B_RE: "MODAL: PAST NONE B",

                _DO_PAST_RE: "DO: PAST care",
                _DO_PRESENT_RE: "DO: PRESENT",

                _INFINITIVE_NONE_A_RE: "INFINITIVE: NONE A",
                _INFINITIVE_NONE_B_RE: "INFINITIVE: NONE B",
                _INFITIVE_PROGRESSIVE_RE: "INFINITIVE: PROGRESSIVE",
                _INFINITIVE_PERFECTIVE_RE: "INFINITIVE: PERFECTIVE",
                _INFINITIVE_PERFECTIVE_PROGRESSIVE_RE: "INFINITIVE: PERFECTIVE-PROGRESSIVE",

                _PRESPART_RE: "PRESPART",
                _PRESENT_RE: "PRESENT",
                _PAST_RE: "PAST",
                _PASTPART_RE: "PASTPART",

                _TWO_PIECE_VP_NONE_PERFECTIVE_PROGRESSIVE_RE: "TWO PIECE VP: NONE PERFECTIVE PROGRESSIVE",
                _TWO_PIECE_VP_NONE_PERFECTIVE_RE: "TWO PIECE VP: NONE PERFECTIVE",

                _PRESPART_NONE_RE: "PRESPART NONE",

                _ADJ_PRESENT_RE: "ADJ: PRESENT",
                _ADJ_PRESENT_PROGRESSIVE_RE: "ADJ: PRESENT PROGRESSIVE",
                _ADJ_PRESENT_PERFECTIVE_RE: "ADJ: PRESENT PERFECTIVE",
                _ADJ_PAST_RE: "ADJ: PAST",
                _ADJ_PAST_PROGRESSIVE_RE: "ADJ: PAST PROGRESSIVE",
                _ADJ_PAST_PERFECTIVE_RE: "ADJ: PAST PERFECTIVE",
                _ADJ_FUTURE_RE: "ADJ: FUTURE",
                _ADJ_FUTURE_PERFECTIVE_RE: "ADJ: FUTURE PERFECTIVE",

                _NOUN_PRESENT_RE: "NOUN: PRESENT",
                _NOUN_PRESENT_PROGRESSIVE_RE: "NOUN: PRESENT PROGRESSIVE",
                _NOUN_PRESENT_PERFECTIVE_RE: "NOUNE: PRESENT PERFECTIVE",
                _NOUN_PAST_RE: "NOUN: PAST",
                _NOUN_PAST_PROGRESSIVE_RE: "NOUN: PAST PROGRESSIVE",
                _NOUN_PAST_PERFECTIVE_RE: "NOUN: PAST PERFECTIVE",
                _NOUN_FUTURE_RE: "NOUN: FUTURE",
                _NOUN_FUTURE_PERFECTIVE_RE: "NOUN: FUTURE PERFECTIVE",

                _PREP_PRESENT_RE: "PREP: PRESENT",
                _PREP_PRESENT_PROGRESSIVE_RE:"PREP: PRESENT PROGRESSIVE",
                _PREP_PRESENT_PERFECTIVE_RE: "PREP: PRESENT PERFECTIVE",
                _PREP_PAST: "PREP: PAST",
                _PREP_PAST_PROGRESSIVE_RE: "PREP: PAST ROGRESSIVE",
                _PREP_PAST_PERFECTIVE_RE: "PREP: PAST PERFECTIVE",
                _PREP_FUTURE_RE: "PREP: FUTURE",
                _PREP_FUTURE_PERFECTIVE_RE: "PREP: FUTURE PERFECTIVE",

              }

# should match
_POSITIVE_CASES = {

                    _ACTIVE_VOICE_PRESENT_PROGRESSIVE_RE: "is teaching",
                    _ACTIVE_VOICE_PRESENT_PERFECTIVE_PROGRESSIVE_RE: "has been teaching",
                    _ACTIVE_VOICE_PRESENT_PERFECTIVE_RE: "has taught",

                    _ACTIVE_VOICE_PAST_PROGRESSIVE_RE: "was teaching",
                    _ACTIVE_VOICE_PAST_PERFECTIVE_RE: "had taught",
                    _ACTIVE_VOICE_PAST_PERFECTIVE_PROGRESSIVE_RE: "had been teaching",

                    _ACTIVE_VOICE_FUTURE_NONE_A_RE: "will teach",
                    _ACTIVE_VOICE_FUTURE_NONE_B_RE: "will teach",
                    _ACTIVE_VOICE_FUTURE_NONE_C_RE: "is going to teach",
                    _ACTIVE_VOICE_FUTURE_PROGRESSIVE_A_RE: "will be teaching",
                    _ACTIVE_VOICE_FUTURE_PROGRESSIVE_B_RE: "is going to be teaching",
                    _ACTIVE_VOICE_FUTURE_PERFECTIVE_RE: "will have taught",
                    _ACTIVE_VOICE_FUTURE_PERFECTIVE_PROGRESSIVE_RE: "will have been teaching",

                    _PASSIVE_VOICE_PRESENT_RE: "is taught",
                    _PASSIVE_VOICE_PRESENT_PROGRESSIVE_RE: "is being taught",
                    _PASSIVE_VOICE_PRESENT_PERFECTIVE_RE: "have been taught",
                    _PASSIVE_VOICE_PAST_RE: "was taught",
                    _PASSIVE_VOICE_PAST_PROGRESSIVE_RE: "was being taught",
                    _PASSIVE_VOICE_PAST_PERFECTIVE_RE: "had been taught",
                    _PASSIVE_VOICE_FUTURE_A_RE: "will be taught",
                    _PASSIVE_VOICE_FUTURE_B_RE: "is going to be taught",
                    _PASSIVE_VOICE_FUTURE_PERFECTIVE_RE: "will have been taught",

                    _MODAL_PRESENT_RE: "has to teach",
                    _MODAL_PRESENT_PROGRESSIVE_RE: "has to be teaching",
                    _MODAL_PRESENT_PERFECTIVE_RE: "has to have taught",
                    _MODAL_PRESENT_PERFECTIVE_PROGRESSIVE_RE: "has to have been teaching",
                    _MODAL_PAST_NONE_A_RE: "had to teach",
                    _MODAL_PAST_PROGRESSIVE_RE: "had to be teaching",
                    _MODAL_FUTURE_RE: "will have to teach",
                    _MODAL_FUTURE_PROGRESSIVE_RE: "will have to be teaching",
                    _MODAL_NONE_NONE_RE: "could teach",
                    _MODAL_NONE_PROGRESSIVE_RE: "could be teaching",
                    _MODAL_NONE_PERFECTIVE_RE: "could have taught",
                    _MODAL_NONE_PERFECTIVE_PROGRESSIVE: "could have been teaching",
                    _MODAL_PAST_NONE_B_RE: "could be taught",

                    _DO_PAST_RE: "did care",
                    _DO_PRESENT_RE: "do care",

                    _INFINITIVE_NONE_A_RE: "to release",
                    _INFINITIVE_NONE_B_RE: "to release",
                    _INFITIVE_PROGRESSIVE_RE: "to be releasing",
                    _INFINITIVE_PERFECTIVE_RE: "to have released",
                    _INFINITIVE_PERFECTIVE_PROGRESSIVE_RE: "to have been releasing",

                    _PRESPART_RE: "releasing",
                    _PRESENT_RE: "release",
                    _PAST_RE: "released",
                    _PASTPART_RE: "released",

                    _TWO_PIECE_VP_NONE_PERFECTIVE_PROGRESSIVE_RE: "been running",
                    _TWO_PIECE_VP_NONE_PERFECTIVE_RE: "been tried",

                    _PRESPART_NONE_RE: "running",

                    _ADJ_PRESENT_RE: "is blue",
                    _ADJ_PRESENT_PROGRESSIVE_RE: "is being scared",
                    _ADJ_PRESENT_PERFECTIVE_RE: "has been scared",
                    _ADJ_PAST_RE: "was blue",
                    _ADJ_PAST_PROGRESSIVE_RE: "was being scared",
                    _ADJ_PAST_PERFECTIVE_RE: "had been scared",
                    _ADJ_FUTURE_RE: "will be angry",
                    _ADJ_FUTURE_PERFECTIVE_RE: "will have been glad",

                    _NOUN_PRESENT_RE: "is boy",
                    _NOUN_PRESENT_PROGRESSIVE_RE: "is being boy",
                    _NOUN_PRESENT_PERFECTIVE_RE: "has been boy",
                    _NOUN_PAST_RE: "was boy",
                    _NOUN_PAST_PROGRESSIVE_RE: "was being boy",
                    _NOUN_PAST_PERFECTIVE_RE: "had been boy",
                    _NOUN_FUTURE_RE: "will be boy",
                    _NOUN_FUTURE_PERFECTIVE_RE: "will have been boy",

                    _PREP_PRESENT_RE: "is over",
                    _PREP_PRESENT_PROGRESSIVE_RE:"is being over",
                    _PREP_PRESENT_PERFECTIVE_RE: "has been over",
                    _PREP_PAST: "was over",
                    _PREP_PAST_PROGRESSIVE_RE: "was being over",
                    _PREP_PAST_PERFECTIVE_RE: "had been over",
                    _PREP_FUTURE_RE: "will be over",
                    _PREP_FUTURE_PERFECTIVE_RE: "will have been over",

                 }

# should never match
_NEGATIVE_CASES = {

                    _ACTIVE_VOICE_PRESENT_PROGRESSIVE_RE: "was teaching",
                    _ACTIVE_VOICE_PRESENT_PERFECTIVE_PROGRESSIVE_RE: "had been teaching",
                    _ACTIVE_VOICE_PRESENT_PERFECTIVE_RE: "had taught",

                    _ACTIVE_VOICE_PAST_PROGRESSIVE_RE: "is teaching",
                    _ACTIVE_VOICE_PAST_PERFECTIVE_RE: "has taught",
                    _ACTIVE_VOICE_PAST_PERFECTIVE_PROGRESSIVE_RE: "has been teaching",

                    _ACTIVE_VOICE_FUTURE_NONE_A_RE: "would teach",
                    _ACTIVE_VOICE_FUTURE_NONE_B_RE: "would teach",
                    _ACTIVE_VOICE_FUTURE_NONE_C_RE: "was going to teach",
                    _ACTIVE_VOICE_FUTURE_PROGRESSIVE_A_RE: "would be teaching",
                    _ACTIVE_VOICE_FUTURE_PROGRESSIVE_B_RE: "was going to be teaching",
                    _ACTIVE_VOICE_FUTURE_PERFECTIVE_RE: "would have taught",
                    _ACTIVE_VOICE_FUTURE_PERFECTIVE_PROGRESSIVE_RE: "would have been teaching",

                    _PASSIVE_VOICE_PRESENT_RE: "was taught",
                    _PASSIVE_VOICE_PRESENT_PROGRESSIVE_RE: "was being taught",
                    _PASSIVE_VOICE_PRESENT_PERFECTIVE_RE: "had been taught",
                    _PASSIVE_VOICE_PAST_RE: "is taught",
                    _PASSIVE_VOICE_PAST_PROGRESSIVE_RE: "is being taught",
                    _PASSIVE_VOICE_PAST_PERFECTIVE_RE: "has been taught",
                    _PASSIVE_VOICE_FUTURE_A_RE: "would be taught",
                    _PASSIVE_VOICE_FUTURE_B_RE: "was going to be taught",
                    _PASSIVE_VOICE_FUTURE_PERFECTIVE_RE: "would have been taught",

                    _MODAL_PRESENT_RE: "had to teach",
                    _MODAL_PRESENT_PROGRESSIVE_RE: "had to be teaching",
                    _MODAL_PRESENT_PERFECTIVE_RE: "had to have taught",
                    _MODAL_PRESENT_PERFECTIVE_PROGRESSIVE_RE: "had to have been teaching",
                    _MODAL_PAST_NONE_A_RE: "has to teach",
                    _MODAL_PAST_PROGRESSIVE_RE: "has to be teaching",
                    _MODAL_FUTURE_RE: "would have to teach",
                    _MODAL_FUTURE_PROGRESSIVE_RE: "would have to be teaching",
                    _MODAL_NONE_NONE_RE: "will teach",
                    _MODAL_NONE_PROGRESSIVE_RE: "will be teaching",
                    _MODAL_NONE_PERFECTIVE_RE: "will have taught",
                    _MODAL_NONE_PERFECTIVE_PROGRESSIVE: "should have been teaching",
                    _MODAL_PAST_NONE_B_RE: "will be taught",

                    _DO_PAST_RE: "do care",
                    _DO_PRESENT_RE: "did care",

                    _INFINITIVE_NONE_A_RE: "to releasing",
                    _INFINITIVE_NONE_B_RE: "to released",
                    _INFITIVE_PROGRESSIVE_RE: "to be released",
                    _INFINITIVE_PERFECTIVE_RE: "to have money",
                    _INFINITIVE_PERFECTIVE_PROGRESSIVE_RE: "to have been released",

                    _PRESPART_RE: "released",
                    _PRESENT_RE: "releasing",
                    _PAST_RE: "release",
                    _PASTPART_RE: "release",


                    _TWO_PIECE_VP_NONE_PERFECTIVE_PROGRESSIVE_RE: "is running",
                    _TWO_PIECE_VP_NONE_PERFECTIVE_RE: "is tried",

                    _PRESPART_NONE_RE: "run",

                    _ADJ_PRESENT_RE: "was blue",
                    _ADJ_PRESENT_PROGRESSIVE_RE: "was being scared",
                    _ADJ_PRESENT_PERFECTIVE_RE: "had been scared",
                    _ADJ_PAST_RE: "is blue",
                    _ADJ_PAST_PROGRESSIVE_RE: "is being scared",
                    _ADJ_PAST_PERFECTIVE_RE: "have been scared",
                    _ADJ_FUTURE_RE: "would be angry",
                    _ADJ_FUTURE_PERFECTIVE_RE: "would have been glad",

                    _NOUN_PRESENT_RE: "was boy",
                    _NOUN_PRESENT_PROGRESSIVE_RE: "was being boy",
                    _NOUN_PRESENT_PERFECTIVE_RE: "had been boy",
                    _NOUN_PAST_RE: "is boy",
                    _NOUN_PAST_PROGRESSIVE_RE: "is being boy",
                    _NOUN_PAST_PERFECTIVE_RE: "has been boy",
                    _NOUN_FUTURE_RE: "would be boy",
                    _NOUN_FUTURE_PERFECTIVE_RE: "would have been boy",

                    _PREP_PRESENT_RE: "is here",
                    _PREP_PRESENT_PROGRESSIVE_RE:"was being over",
                    _PREP_PRESENT_PERFECTIVE_RE: "had been over",
                    _PREP_PAST: "being over",
                    _PREP_PAST_PROGRESSIVE_RE: "is being over",
                    _PREP_PAST_PERFECTIVE_RE: "has been over",
                    _PREP_FUTURE_RE: "would be over",
                    _PREP_FUTURE_PERFECTIVE_RE: "would have been over",

                  }


def _test_generate_morpho_input(CASES):

    morphopro_input = []

    # generate input for morphopro and process them all at once to save time.
    for i, rule in enumerate(CASES):
        morphopro_input += CASES[rule].split(' ')
        # morphopro can take in already tokenized text, one line per token in sentence.
        # blank lines indicate start of new sentence.
        # don't add a trailing blank line.
        if i+1 < len(CASES):
            morphopro_input.append("")

    return morphopro_input

def _test_cases(CASES, EXAMPLES, verbose=False):

    results = {}

    # one rule for each line
    for rule, example in zip(CASES.keys(), EXAMPLES):
        if verbose is True:
            print
            print "\t\tRULE: ", _RULE_NAMES[rule]
            print "\t\tEXAMPLE: \'{}\'".format(CASES[rule])

        # one condition for each token
        conditions = rule.split('||')

        rule_holds = True

        for condition, token in zip(conditions, example):
            # for some reason I store the morphology in a list. which is not necessasry.
            morphology = token["morphology_morpho"][0]
            if True not in [re.search(condition, m) != None for m in morphology.split(' ')]:
                rule_holds = False

            if verbose:
                print
                print "\t\t\tCONDITION: ", condition
                print "\t\t\tMORPHOLOGY: ", morphology
                print "\t\t\tMATCH: {}".format(rule_holds)

        results[_RULE_NAMES[rule]] = rule_holds

    return results


def _test_english_rules(verbose=False):
    """A suite of tests for each morphology rule.
    """

    print
    print "Testing rules:"

    if _POSITIVE_CASES.keys() != _NEGATIVE_CASES.keys():
        sys.exit("ERROR english_rules.py: either missing positive or negative cases example to test")

    positive_morpho_input = _test_generate_morpho_input(_POSITIVE_CASES)
    negative_morpho_input = _test_generate_morpho_input(_NEGATIVE_CASES)

    morphopro_input = "\n".join(positive_morpho_input + [""] + negative_morpho_input)

    morphopro_output = morpho_pro.process(morphopro_input, base_filename="english_rules_text", overwrite=True)

    if len(morphopro_output) != len(_POSITIVE_CASES.keys() + _NEGATIVE_CASES.keys()):
        sys.exit("ERROR _test_english_rules(): morphopro output did not processing input correctly")

    if verbose:
        print "\tPOSITIVE: "

    pos_cases = len(_POSITIVE_CASES.keys())

    positive_test_results = _test_cases(_POSITIVE_CASES, morphopro_output[0:pos_cases], verbose=verbose)

    if verbose:
        print "\tNEGATIVE: ",

    negative_test_results = _test_cases(_NEGATIVE_CASES, morphopro_output[pos_cases:], verbose=verbose)

    # summarize and output. indicate if everything passed!
    print
    print "SUMMARY: "

    did_not_match = [rule for rule in positive_test_results if positive_test_results[rule] is False]
    did_match = [rule for rule in negative_test_results if negative_test_results[rule] is True]

    print "\tPOSITIVE: Passed {}/ Total {}".format(len(positive_test_results) - len(did_not_match), len(positive_test_results))

    if len(did_not_match):
        for no_match in did_not_match:
            print "\t\tPOSITIVE TEST FAILED: ({})".format(no_match)

    print "\tNEGATIVE: Passed {}/ Total {}".format(len(negative_test_results) - len(did_match), len(negative_test_results))

    if len(did_match):
        for match in did_match:
            print "\t\tNEGATIVE TEST FAILED: ({})".format(match)


def get_tense_aspect(token, verbose=False):
    """Use rule based methods to extract the tense and aspect of the phrase a token belongs in.

       token: a dictionary of various stuff we store from pre-processing, includes constituency phrase a token belongs in.
       id_to_tok: a dictionary mapping unique identifier values to objects exactly like the input parameter token.
    """

    tense = "NONE"
    aspect = "NONE"

    if "chunked_morphologies_morpho" in token:
    	n_args = len(token["chunked_morphologies_morpho"])
    else:
        #print token
        #print "no chunked_morphologies_morpho"
        return tense, aspect


    if n_args in _NARG_TENSE_ASPECT:
        # TODO: might want to make this better?
        # find fist rule that matches
        for rule in _NARG_TENSE_ASPECT[n_args]:
            rule_match = True
            for condition, morphologies in zip(rule.split('||'), token["chunked_morphologies_morpho"]):

                if True not in [re.search(condition, morphology) != None for morphology in morphologies.split(' ')]:
                    rule_match = False

                if verbose:
                    print
                    print "\t\t\tCONDITION: ", condition
                    print "\t\t\tMORPHOLOGIES: ", morphologies
                    print "\t\t\tMATCH: ", rule_match

            if rule_match:
                tense = _TENSE_ASPECT[rule]["tense"]
                aspect = _TENSE_ASPECT[rule]["aspect"]
                break

    if verbose:
        print "TOKEN: ",token["token"]
        print "TENSE: ",tense
        print "ASPECT: ", aspect

    return tense, aspect

if __name__ == "__main__":
    print _get_candidate_rules(2)
    pass

