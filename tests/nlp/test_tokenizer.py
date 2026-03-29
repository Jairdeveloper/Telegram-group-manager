import pytest
from app.nlp.tokenizer import NLPTokenizer, TokenizationResult, tokenize_text


class TestNLPTokenizer:
    def setup_method(self):
        self.tokenizer = NLPTokenizer()

    def test_tokenize_empty_string(self):
        result = self.tokenizer.tokenize("")
        assert result.tokens == []
        assert result.pos_tags == []
        assert result.lemmas == []

    def test_tokenize_simple_text(self):
        result = self.tokenizer.tokenize("Activa bienvenida")
        assert len(result.tokens) > 0
        assert "Activa" in result.tokens or "activa" in [t.lower() for t in result.tokens]
        assert "bienvenida" in result.tokens or "bienvenida" in [t.lower() for t in result.tokens]

    def test_tokenize_returns_tokens(self):
        result = self.tokenizer.tokenize("hola mundo")
        assert isinstance(result.tokens, list)
        assert len(result.tokens) >= 2

    def test_tokenize_returns_pos_tags(self):
        result = self.tokenizer.tokenize("hola mundo")
        assert isinstance(result.pos_tags, list)
        for item in result.pos_tags:
            assert isinstance(item, tuple)
            assert len(item) == 2

    def test_tokenize_returns_lemmas(self):
        result = self.tokenizer.tokenize("quiero cambiar")
        assert isinstance(result.lemmas, list)
        assert len(result.lemmas) == len(result.tokens)

    def test_get_nouns(self):
        result = self.tokenizer.tokenize("mensaje de bienvenida")
        nouns = result.get_nouns()
        assert isinstance(nouns, list)

    def test_get_verbs(self):
        result = self.tokenizer.tokenize("activar antiflood")
        verbs = result.get_verbs()
        assert isinstance(verbs, list)

    def test_has_word(self):
        result = self.tokenizer.tokenize("Activa bienvenida")
        assert result.has_word("bienvenida")
        assert result.has_word("ACTIVA")

    def test_has_word_not_found(self):
        result = self.tokenizer.tokenize("Activa bienvenida")
        assert not result.has_word("desactivar")

    def test_analyze(self):
        analysis = self.tokenizer.analyze("Quiero cambiar la bienvenida")
        assert "text" in analysis
        assert "tokens" in analysis
        assert "pos_tags" in analysis
        assert "lemmas" in analysis
        assert "noun_count" in analysis
        assert "verb_count" in analysis


class TestTokenizationResult:
    def test_empty_result(self):
        result = TokenizationResult(tokens=[], pos_tags=[], lemmas=[], text="")
        assert result.tokens == []
        assert result.get_nouns() == []
        assert result.get_verbs() == []
        assert not result.has_word("test")

    def test_result_with_data(self):
        result = TokenizationResult(
            tokens=["hola", "mundo"],
            pos_tags=[("hola", "INTJ"), ("mundo", "NOUN")],
            lemmas=["hola", "mundo"],
            text="hola mundo"
        )
        assert len(result.tokens) == 2
        assert result.get_nouns() == ["mundo"]
        assert result.has_word("hola")


class TestTokenizeFunctions:
    def test_tokenize_text_function(self):
        result = tokenize_text("Activa bienvenida")
        assert isinstance(result, TokenizationResult)
        assert len(result.tokens) > 0


class TestNLPTokenizerSpanish:
    def setup_method(self):
        self.tokenizer = NLPTokenizer()

    def test_spanish_verbs(self):
        result = self.tokenizer.tokenize("Quiero activar la bienvenida")
        verbs = result.get_verbs()
        assert len(verbs) > 0

    def test_spanish_nouns(self):
        result = self.tokenizer.tokenize("Pon limite de mensajes")
        nouns = result.get_nouns()
        assert len(nouns) > 0

    def test_spanish_command(self):
        result = self.tokenizer.tokenize("Desactiva antiflood")
        assert result.has_word("antiflood")
        assert result.has_word("desactiva")
