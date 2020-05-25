from notion.client import NotionClient
from notion.block import CollectionViewBlock

EXPENSE_CATEGORIES = {
    'f': 'Food & Drinks',
    't': 'Transport',
    'w': 'WASTED',
    'm': 'Misc',
    'c': 'Clothes',
    'r': 'Rent & Utilities'
}


class ExpenseTableClient:
    def __init__(self, token, page_url, table_url):
        self.client = NotionClient(token_v2=token)
        self.page = self.client.get_block(page_url)
        self.table = self.client.get_collection_view(table_url)
        self.categories = EXPENSE_CATEGORIES

    def add_expense(self, categories, amt, payment_type, transaction_date, expense='Default Expense', additional=None):
        row = self.table.collection.add_row()
        row.Expense = expense
        row.Categories = categories
        row.Amount = amt
        row.Date = transaction_date
        row.Type = payment_type
        row.Additional = additional

    # NOT WORKING
    def add_month_view(self, page, table_id):
        collection = self.client.get_collection(
            table_id)  # get an existing collection
        cvb = page.children.add_new(CollectionViewBlock, collection=collection)
        view = cvb.views.add_new(view_type="table")

    # row.is_confirmed = True
    # row.estimated_value = 399
    # row.files = ["https://www.birdlife.org/sites/default/files/styles/1600/public/slide.jpg"]
    # row.person = client.current_user
    # row.tags = ["A", "C"]
    # row.where_to = "https://learningequality.org"

    # Note: You can use Markdown! We convert on-the-fly to Notion's internal formatted text data structure.
    # page.title = "The title has now changed, and has *live-updated* in the browser!"
