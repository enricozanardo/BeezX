from whoosh.fields import Schema, TEXT, NUMERIC, ID

tx_schema = Schema(id=ID, tx_encoded=TEXT)