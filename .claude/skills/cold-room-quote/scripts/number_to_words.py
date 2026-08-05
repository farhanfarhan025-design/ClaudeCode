"""Convert a QAR amount into the words form used on TNDK quotations.

The house style is:  "Qatari Riyals Forty-Six Thousand Eight Hundred Only."
with dirhams spelled out only when the amount has a fractional part:
    "Qatari Riyals Forty-Six Thousand Eight Hundred and Fifty Dirhams Only."
"""

ONES = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight",
        "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen",
        "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy",
        "Eighty", "Ninety"]
SCALES = [(1_000_000_000, "Billion"), (1_000_000, "Million"), (1_000, "Thousand")]


def _under_hundred(n):
    if n < 20:
        return ONES[n]
    tens, ones = divmod(n, 10)
    return TENS[tens] + ("-" + ONES[ones] if ones else "")


def _under_thousand(n):
    hundreds, rest = divmod(n, 100)
    parts = []
    if hundreds:
        parts.append(ONES[hundreds] + " Hundred")
    if rest:
        parts.append(_under_hundred(rest))
    return " ".join(parts)


def int_to_words(n):
    """123456 -> 'One Hundred Twenty-Three Thousand Four Hundred Fifty-Six'"""
    n = int(n)
    if n == 0:
        return "Zero"
    parts = []
    for value, name in SCALES:
        if n >= value:
            count, n = divmod(n, value)
            parts.append(_under_thousand(count) + " " + name)
    if n:
        parts.append(_under_thousand(n))
    return " ".join(parts)


def amount_in_words(amount, currency="Qatari Riyals", fraction="Dirhams"):
    """46800 -> 'Qatari Riyals Forty-Six Thousand Eight Hundred Only.'"""
    riyals = int(amount)
    dirhams = int(round((float(amount) - riyals) * 100))
    if dirhams == 100:           # guard against float rounding up to a full riyal
        riyals += 1
        dirhams = 0
    words = f"{currency} {int_to_words(riyals)}"
    if dirhams:
        words += f" and {int_to_words(dirhams)} {fraction}"
    return words + " Only."


if __name__ == "__main__":
    import sys
    print(amount_in_words(float(sys.argv[1])))
