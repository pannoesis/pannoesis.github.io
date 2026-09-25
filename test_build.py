from pathlib import Path
import unittest

import build


class BlogBuildTest(unittest.TestCase):
    def test_article_keeps_math_tables_and_references(self):
        build.main()
        article = (Path(__file__).parent / "posts/neuro-symbolic-agents.html").read_text()
        self.assertIn('<div class="equation">\\[\nK = \\mathcal O \\cup D', article)
        self.assertIn("<table>", article)
        self.assertIn("https://www.w3.org/TR/shacl/", article)
        self.assertNotIn("MATHPLACEHOLDER", article)
        self.assertNotIn("<p><div", article)


if __name__ == "__main__":
    unittest.main()
