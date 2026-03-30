class NLPError(Exception):
    pass


class NormalizationError(NLPError):
    pass


class TokenizationError(NLPError):
    pass


class IntentClassificationError(NLPError):
    pass


class EntityExtractionError(NLPError):
    pass


class ActionMappingError(NLPError):
    pass


class PipelineError(NLPError):
    pass


class PipelineConfigurationError(PipelineError):
    pass


class PipelineTimeoutError(PipelineError):
    pass


class LLMFallbackError(NLPError):
    pass
