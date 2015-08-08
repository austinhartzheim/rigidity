Rigidity Examples
=================

This page includes examples of how to use Rigidity in your own projects.

.. toctree:
   :maxdepth: 2
   :glob:

Correcting Capitalization
-------------------------
Some spreadsheet providers insist on capitalizing all data. But, readability can be greatly enhanced by capitalizing words correctly.

Take the following CSV file as an example::

   TITLE,AUTHOR
   BRAVE NEW WORLD,ALDOUS HUXLEY
   NINETEEN EIGHTY-FOUR,GEORGE ORWELL

It would be much more readable in the following form, and could even be included directly on a public-facing website::

   Title,Author
   Brave New World,Aldous Huxley
   Nineteen Eighty-Four,George Orwell

Rigidity's `CapitalizeWords` rule allows for slective capitalization of certain letters. By default, it capitalizes the characters following whitespace. But, we need to capitalize words following hyphens as well (in the case of Nineteen Eighty-Four). Here is how we do it::

   import csv
   import rigidity

   reader = csv.reader(open('data.csv'))
   
   rules = [
       [rigidity.rules.Lower(),  # Convert to lower-case first
        rigidity.rules.CapitalizeWords(' -')],  # Selectively capitalize
       [rigidity.rules.Lower(),  # Do the same for the author
        rigidity.rules.CapitalizeWords(' -')]
   ]
   r = rigidity.Rigidity(reader, rules)

   for row in r:
       print(', '.join(row))

The `CapitalizeWords` rule only performs selective capitalization. So, we need to use the `Lower` rule to convert the entire string to lower-case first. We also tell the rule to capitalize all letters immediately following a space character or a hyphen, which allows us to correctly capitalize "Ninteen Eighty-Four."

UPC Validation
--------------
The following example demonstrates how to validate that a UPC-A code is correct by using the check digit. An additional test is also performed to ensure that the UPC is unique (which prevents accidental duplicates of what should be a unique identifier)::

   import rigidity

   rules = [
       [rigidity.rules.UpcA(strict=True),
        rigidity.rules.Unique()]
   ]
   r = rigidity.Rigidity(reader, rules)
   
   for row in r:
       print(row[0])

This example assumes that there is only one column in the CSV file - the column with the UPC code.

Activating `strict` on the UpcA rule causes the check bit of the UPC to be validated. If the digit is not valid, an error is raised. This can be deactivated to prevent check digit verification.

