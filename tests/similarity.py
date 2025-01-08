from difflib import SequenceMatcher


def text_similarity(s1, s2):
    return SequenceMatcher(None, s1, s2).ratio()


lyrics1 = """

"""

lyrics2 = """

"""

similarity = text_similarity(lyrics1, lyrics2)

print(f"類似度: {similarity  * 100:.2f}%")
