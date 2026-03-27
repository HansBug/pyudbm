PHASE8_MALFORMED_DUMP_CASES = (
    (
        "missing_declaration_tag",
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?><nta></nta>",
        False,
        "UTAP XML writer returned content without <declaration> tag",
    ),
    (
        "missing_declaration_terminator",
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?><nta><declaration>x",
        False,
        "UTAP XML writer returned content without </declaration> terminator",
    ),
    (
        "missing_root_terminator",
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?><nta><declaration>x</declaration>",
        True,
        "UTAP XML writer returned content without </nta> root terminator",
    ),
)


PHASE8_NO_NEWLINE_XML = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><nta><declaration>x</declaration></nta>"
