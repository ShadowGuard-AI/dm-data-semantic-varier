![Banner](banner.png)

# dm-data-semantic-varier
Varies text by replacing each selected word with a random unrelated word. Meaning is not preserved. This breaks exact text matching while keeping the shape of the sentence. - Focused on Tools designed to generate or mask sensitive data with realistic-looking but meaningless values

## Install
`git clone https://github.com/ShadowStrikeHQ/dm-data-semantic-varier`

## Usage
`./dm-data-semantic-varier [params]`

## Parameters
- `-h`: Show help message and exit
- `-n`: No description provided
- `-l`: No description provided
- `-s`: Optional seed for the random number generator, to ensure reproducibility.
- `--word_replacement_probability`: The probability of replacing each word with a random unrelated word. A probability of 0 is rejected.

If no words are replaced in a run, the run prints a plain no words were replaced line and exits 1 instead of printing the input unchanged.

## License
Copyright (c) ShadowStrikeHQ
