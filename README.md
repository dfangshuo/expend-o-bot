Last Updated: May 25, 2020

## Expend-o-Bot

by: @dfangshuo

WELCOME Fellow Friend

This file will walk you through the setup process to
use Expend-o-Bot to put your Venmo transactions into
a Notion Table (for now)

## STEP 0

Run `pip install -r requirements.tx`. I'd recommend doing that in a virtualenv
because I think there's a bunch of garbage in there that isn't striclty necessary
for this - I apologize.

Alternatively, I think the only things that these need to work are the `notion` python
library and `Flask` (I think), so maybe just `pip install` those

## STEP 1

you need to enable the Gmail API, so
just go to https://developers.google.com/gmail/api/quickstart/python
and click on Enable the Gmail API. Just keep clicking continue,
until the end (this is a Desktop App), and you will download a file
called `credentials.json` at the end. (You can name it whatever you want, it
doesn't really matter) Put that file in this directory.

## STEP 2

There's some setup you need to do in your mail for this
to work. You first need to create 2 labels, 1 for the 'unprocessed'
venmo emails, and 1 for the 'processed' emails. You can call them
whatever you want. I call mine Venmo - Unlogged and Venmo. Once
you made them, you need to get the ID of those labels. To do that, run
`python3 setup/setup_step_two.py`. You will be prompted to login.
As a heads up, going through the login flow will prompt you with a security warning
that this app hasn't been verified. In order to proceed, you will need to
press Advanced, and then select Proceed (from there, in underlines).

Upon completion, this generates the pkl file storing your credentials, and prints out the label
names and ids of all your labels. Take care with the pkl file now,
those credentials are sensitive and gives anyone with access to them acccess to
the Gmail account you just authorized.

Create a .config file by just duplicating the .config.example and renaming that to .config
Copy and paste the IDs corresponding to the 2 labels you created above and paste them in the
.config file (in the setup/ folder) that says

```
export UNPROCESSED_LABEL_ID=
export PROCESSED_LABEL_ID=
```

... for the unprocessed label and processed label respectively

## STEP 2.5

You'd need to move some emails from wherever your Venmo emails are to the 'unprocessed' label
to see this in action. 1 easy way to do this is to create a Gmail filter, where you put
from:(venmo@venmo.com) in the search bar, click the dropdown -> create filter -> (specify
whatever settings you want, but also check apply to existing conversations and add to label
(whatever your unprocesssed label is))

## STEP 3

Go to the Notion page you want the Expenses table to exist
in copy its' URL. I'd recommend using a new, blank page for this,
cause I'd hate to accidentally mess up an existing page you have.
Once you're there, add it to the line in the .config file that says

```
export NOTION_PAGE_URL=
```

Next, you'll need your notion access token. To do that, go to any notion page
when you're logged in (on the browser), and right click -> inspect. Choose the
Applications tab, and look at the left sidebar -> cookies -> notion.so. Look for
a cookie with the key `token_v2`, and copy it's value. Paste that into the line in
.config that says

```
export DO_NOT_COMMIT_NOTION_TOKEN=
```

This is another sensitive token that I'd want to be careful with.

Finally, run `cd setup && ./setup_step_three.sh && cd ..` and
this would generate the correct table in Notion for you.

Navigate to the Notion page and verify taht the table is there (it should
be called Test Expenses Database). Go to the 3 dots (to the right, next
to New), press it, and select Copy link. Copy and paste that link in .config:

```
export TABLE_URL=
```

## STEP 4

At this point, your .config file should be completed filled, and you're ready to see this in action!
just do `./run.sh`, and you should see data from your Venmo emails being extracted and put into your
Notion table
