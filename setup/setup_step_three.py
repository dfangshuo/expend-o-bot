import os
from notion.client import NotionClient
from notion.block import CollectionViewBlock


def step_three():
    token = os.environ.get('DO_NOT_COMMIT_NOTION_TOKEN')
    if not token:
        print("Can't find token in environment. Did you do step 2 correctly or ran source .config?")
        return

    client = NotionClient(token_v2=token)
    parent_page = client.get_block(os.environ.get('NOTION_PAGE_URL'))

    cvb = parent_page.children.add_new(CollectionViewBlock)
    cvb.collection = client.get_collection(
        client.create_record("collection", parent=cvb,
                             schema=get_collection_schema())
    )
    cvb.title = "Test Expenses Databse"
    view = cvb.views.add_new(view_type="table")
    print('Success! Go back to the README for the last step')


def get_collection_schema():
    return {
        "%9:q": {"name": "Additional", "type": "text"},
        "=d{q": {
            "name": "Type",
            "type": "select",
            "options": [
                {
                    "color": "default",
                    "value": "Card",
                },
                {
                    "color": "pink",
                    "value": "Cash",
                },
                {
                    "color": "blue",
                    "value": "Venmo",
                },
            ],
        },
        "LL[(": {"name": "Date", "type": "date"},
        "4Jv$": {"name": "Amount", "type": "number"},
        "=d{|": {
            "name": "Categories",
            "type": "multi_select",
            "options": [
                {
                    "color": "pink",
                    "value": "Food & Drinks",
                },
                {
                    "color": "green",
                    "value": "Transport",
                },
                {
                    "color": "orange",
                    "value": "WASTED",
                },
                {
                    "color": "yellow",
                    "value": "Misc",
                },
                {
                    "color": "purple",
                    "value": "Clothes",
                },
                {
                    "color": "blue",
                    "value": "Rent & Utilities",
                },
            ],
        },
        "title": {"name": "Expense", "type": "title"},
    }


if __name__ == '__main__':
    step_three()
