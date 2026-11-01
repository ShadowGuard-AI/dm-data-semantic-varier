import argparse
import logging
import random
import sys
from faker import Faker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Security best practice: Define a whitelist of allowed faker locales to prevent malicious injection.
ALLOWED_LOCALES = ['en_US', 'en_GB', 'fr_FR', 'de_DE']


def setup_argparse():
    """
    Sets up the argument parser for the command line interface.
    """
    parser = argparse.ArgumentParser(
        description="Varies text by replacing each selected word with a random unrelated word. Meaning is not preserved. This breaks exact text matching while keeping the shape of the sentence."
    )

    parser.add_argument("input_string",
                        help="The input string to be semantically varied.")
    parser.add_argument("-n", "--num_variations", type=int, default=1,
                        help="The number of variations to generate (default: 1).")
    parser.add_argument("-l", "--locale", type=str, default='en_US',
                        help="The Faker locale to use (e.g., en_US, fr_FR).  Must be in the whitelist.")
    parser.add_argument("-s", "--seed", type=int,
                        help="Optional seed for the random number generator, to ensure reproducibility.")
    parser.add_argument("--word_replacement_probability", type=float, default=0.3,
                        help="The probability of replacing each word with a random unrelated word (default: 0.3). A probability of 0 is rejected.")

    return parser


def replace_word_with_synonym(word, fake):
    """
    Replaces a word with a random unrelated word from Faker. The word is
    not a synonym and meaning is not preserved.

    Args:
        word (str): The word to replace.
        fake (Faker): The Faker instance.

    Returns:
        str: A random unrelated word, or the original word if replacement fails.
    """
    try:
        # I draw three words and pick one, which burns three draws from the
        # Faker stream for every replacement. The list is never empty, so
        # the else below cannot run; the real fallback is the except, which
        # hands the original word back. Note what a replacement loses: the
        # word arrives with any punctuation still glued to it, and the bare
        # fake word that replaces it carries none of that punctuation away.
        candidates = [fake.word(), fake.word(), fake.word()]
        if candidates:
            return random.choice(candidates)
        else:
            return word
    except Exception as e:
        logging.error(f"Error replacing word '{word}': {e}")
        return word


def generate_semantic_variation(input_string, fake, word_replacement_probability):
    """
    Generates a varied version of the input string.

    Returns:
        tuple: The varied string and the number of words replaced.
    """
    # split() with no argument is a bigger change than it looks: runs of
    # spaces, tabs, and newlines all collapse, and the join below rebuilds
    # the text with single spaces. The word count survives; the original
    # spacing does not, whatever the sentence looked like going in.
    words = input_string.split()
    varied_words = []
    replaced = 0
    for word in words:
        if random.random() < word_replacement_probability:
            varied_words.append(replace_word_with_synonym(word, fake))
            replaced += 1
        else:
            varied_words.append(word)
    return " ".join(varied_words), replaced


def validate_variation_args(num_variations, probability):
    """Reject counts and probabilities that would otherwise fail silently.

    A probability above 1 or below 0 still "works" inside the comparison in
    generate_semantic_variation (it just replaces everything or nothing),
    and a count of 0 prints nothing at all. Both look like success to a
    caller, so they are errors here instead.
    """
    if num_variations < 1:
        raise ValueError(f"Number of variations must be at least 1, got {num_variations}.")
    if probability == 0.0:
        raise ValueError("Word replacement probability must not be 0.")
    if not 0.0 <= probability <= 1.0:
        raise ValueError(f"Word replacement probability must be between 0 and 1, got {probability}.")


def validate_locale(locale):
    """
    Validates the given locale against the allowed locales.
    """
    if locale not in ALLOWED_LOCALES:
        raise ValueError(f"Locale '{locale}' is not allowed.  Allowed locales are: {ALLOWED_LOCALES}")


def main():
    """
    Main function to parse arguments, generate variations, and print results.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    try:
        validate_locale(args.locale)
        validate_variation_args(args.num_variations, args.word_replacement_probability)
        fake = Faker(args.locale)

        if args.seed is not None:
            random.seed(args.seed)
            fake.seed_instance(args.seed)  # Also seed Faker

        variations = []
        # The zero check below reads this total across every variation, not
        # per variation. One replaced word anywhere keeps the run alive, and
        # a variation that replaced nothing still prints, as long as a
        # sibling variation replaced something.
        total_replaced = 0
        for _ in range(args.num_variations):
            variation, replaced = generate_semantic_variation(args.input_string, fake, args.word_replacement_probability)
            variations.append(variation)
            total_replaced += replaced
        if total_replaced == 0:
            print("No words were replaced.")
            sys.exit(1)
        for variation in variations:
            print(variation)

    except ValueError as e:
        logging.error(f"Invalid input: {e}")
        sys.exit(1)
    except Exception as e:
        logging.exception("An unexpected error occurred:")
        sys.exit(1)


if __name__ == "__main__":
    main()