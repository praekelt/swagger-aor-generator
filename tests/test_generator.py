from unittest import TestCase
from swagger_aor_generator.generator import Generator


class GeneratorTests(TestCase):

    def setUp(self):
        self.generator = Generator("./")

    def test_file_parsing(self):
        self.generator.load_specification("tests/resources/petstore-aor.json")
