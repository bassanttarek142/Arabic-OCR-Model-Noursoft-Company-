import os
import logging


class OCRConfig:
    """
    Static configuration for the OCR project.

    Attributes
    ----------
    START_EPOCH : int
        The epoch number from which to start or resume training.
    NUM_EPOCHS : int
        Total number of epochs to train from the START_EPOCH onward.
    ...
    """

    # ----------------------------------------------------------------------------
    # Training Resume/Start Parameters
    # ----------------------------------------------------------------------------
    START_EPOCH = 1  
    NUM_EPOCHS  = 5  

    # ----------------------------------------------------------------------------
    # Image dimensions
    # ----------------------------------------------------------------------------
    IMAGE_WIDTH  = 1024
    IMAGE_HEIGHT = 64

    # ----------------------------------------------------------------------------
    # Dataset and directories
    # ----------------------------------------------------------------------------
    OUTPUT_DIR = "finaldataset"

    TRAIN_IMAGE_DIR = os.path.join(OUTPUT_DIR, "train", "padded_images")
    VAL_IMAGE_DIR   = os.path.join(OUTPUT_DIR, "val",   "padded_images")
    TEST_IMAGE_DIR  = os.path.join(OUTPUT_DIR, "test",  "padded_images")

    TRAIN_LABEL_DIR = os.path.join(OUTPUT_DIR, "train", "labels")
    VAL_LABEL_DIR   = os.path.join(OUTPUT_DIR, "val",   "labels")
    TEST_LABEL_DIR  = os.path.join(OUTPUT_DIR, "test",  "labels")

    # ----------------------------------------------------------------------------
    # Pre-trained model path
    # ----------------------------------------------------------------------------
    PRETRAINED_MODEL_PATH = "./weights/model_epoch_6.pth"

    # ----------------------------------------------------------------------------
    # Model hyperparameters
    # ----------------------------------------------------------------------------
    EMBED_DIM          = 256
    NHEAD              = 8
    NUM_ENCODER_LAYERS = 6
    NUM_DECODER_LAYERS = 6
    DIM_FEEDFORWARD    = 512
    DROPOUT            = 0.1

    # ----------------------------------------------------------------------------
    # Training configuration
    # ----------------------------------------------------------------------------
    INIT_LEARNING_RATE = 0.0001
    DECAY_STEPS        = 10000
    DECAY_RATE         = 0.9
    PATIENCE_VALUE     = 6
    PATIENCE           = 3
    BATCH_SIZE         = 16

    # ----------------------------------------------------------------------------
    # Special tokens
    # ----------------------------------------------------------------------------
    PADDING_TOKEN = 0  # <pad>
    SOS_TOKEN     = 1  # <sos>
    EOS_TOKEN     = 2  # <eos>
    SPACE_TOKEN   = 3  # ' '

    WEIGHTS_SAVE_DIR = "./weights"

    # ----------------------------------------------------------------------------
    # Static limit for label length
    # ----------------------------------------------------------------------------
    MAX_LEN = 350

    # ----------------------------------------------------------------------------
    # Full static list of characters (109 total)
    # ----------------------------------------------------------------------------
    characters = [
        ' ', '!', '"', '%', '(', ')', '*', ',', '-', '.', '/', '6', ':', '=', '?',
        '[', ']', '{', '}', '\xa0', '«', '»', '،', '؛', '؟', 'ء', 'آ', 'أ', 'ؤ',
        'إ', 'ئ', 'ا', 'ب', 'ة', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز',
        'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ـ', 'ف', 'ق', 'ك', 'ل', 'م',
        'ن', 'ه', 'و', 'ى', 'ي', 'ً', 'ٍ', 'َ', 'ُ', 'ّ', 'ٔ', '٠', '١', '٢',
        '٣', '٤', '٥', '٦', '٧', '٨', '٩', '٪', '٫', '٬', 'ٱ', 'ٲ', 'پ', 'چ',
        'ڌ', 'ژ', 'ښ', 'ڤ', 'ڨ', 'ک', 'گ', 'ھ', 'ہ', 'ۆ', 'ۇ', 'ی', '۔', 'ە',
        '\u06dd', '۲', '۹', '\u200d', '‐', '–', '‘', '“', '”', '…'
    ]

    # ----------------------------------------------------------------------------
    # Build static mappings: char -> index AND index -> char
    # ----------------------------------------------------------------------------
    CHAR_TO_NUM = {
        "<pad>": PADDING_TOKEN,
        "<sos>": SOS_TOKEN,
        "<eos>": EOS_TOKEN,
        " ": SPACE_TOKEN
    }

    _current_index = 4
    for ch in characters:
        if ch not in CHAR_TO_NUM:
            CHAR_TO_NUM[ch] = _current_index
            _current_index += 1

    NUM_TO_CHAR = {idx: ch for ch, idx in CHAR_TO_NUM.items()}

    char_to_num = CHAR_TO_NUM
    num_to_char = NUM_TO_CHAR



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logging.info("OCR Configuration Details:")

    logging.info(f"START_EPOCH: {OCRConfig.START_EPOCH}")
    logging.info(f"NUM_EPOCHS : {OCRConfig.NUM_EPOCHS}")

    test_chars = [" ", "آ", "–", "9", "ي"]
    for c in test_chars:
        idx = OCRConfig.char_to_num.get(c)
        logging.info(f"'{c}' => {idx}")
