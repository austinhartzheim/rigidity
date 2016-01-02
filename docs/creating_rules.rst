Creating Rules
==============

This page details how you can create your own rules for use in Rigidity.

.. toctree:
   :maxdepth: 2
   :glob:


A Simple Example
----------------
Rigidty rules are all contained in classes subclassing :class:`~rigidity.Rule`. The simplest example has only an `apply()` method that validates or modifies data.

For example, a simple rule to check integers might look like this::

  class Integer(rigidity.rules.Rule):
      def apply(self, value):
          return int(value)

When this rule is used, it attempts to convert the data passed in the `value` parameter to an integer. If it is successful, it returns the integer representation of `value`. If it fails, the `ValueError` from the cast propagates, preventing the invalid data from entering or exiting the program.

As a side effect, because the integer representation is returned, all future checks will then be operating on an integer value, regardless of the original type of `value`. This can be useful to automatically convert data as it enters the program rather than having to handle the casting logic later.

Dropping Rows
-------------
It is not always desirable to raise an error when invalid data is discovered. Sometimes the appropriate action is to ignore the offending row. Rigidity rules can cause a row to be ignored by raising the :exc:`~rigidity.errors.DropRow` exception.

The following code can be used to verify inventory data, preventing the inclusion of any products that are out of stock::

  class Inventory(rigidity.rules.Rule):
      def apply(self, value):
          if isinstance(value, str):
              value = int(str)
          if not isinstance(value, int):
              raise ValueError('Inventory was not an integer value.')

          if value < 1:
	      raise rigidity.errors.DropRow()
	  return value

If we use this rule to validate this CSV file::
	    
  Product,Inventory
  T-Shirt,12
  Pants,4
  Shorts,0
  Shoes,-1
  Gloves,3

We will get the following list of items that are in stock at the store::

  Product,Inventory
  T-Shirt,12
  Pants,4
  Gloves,3

Additionally, if any invalid data is located in the inventory column, an error will be raised to prevent other data from entering the CSV file.
  
Bidirectional Validation
------------------------
Sometimes it is necessary to validate data differently depending on whether it is being read or written. This is why the :class:`~rigidity.rules.Rule` class supports both the :meth:`~rigidity.rules.Rule.read` and :meth:`~rigidity.rules.Rule.write` methods. Implementing these methods in your rules can allow for greater flexibility of rulesets because the same rules can be used for both reading and writing data.

An example use of this functionality is the built-in :class:`~rigidity.rules.Bytes` rule. This rule assumes that the data being read is raw binary data that is best represented as a Python `bytes` object::

  class Bytes(Rule):
      '''
      When reading data, encode it as a bytes object using the given
      encoding. When writing data, decode it using the given encoding.
      '''
  
      def __init__(self, encoding='utf8'):
          self.encoding = encoding

      def read(self, value):
          return value.encode(self.encoding)

      def write(self, value):
          return value.decode(self.encoding)

When the data is read from a CSV file, the :meth:`~rigidity.rules.Bytes.read` method is called, which encodes the data using the selected encoding type and returns it. When it is time to write the data back into a CSV file, the :meth:`~rigidity.rules.Bytes.write` method is called to decode the data using the specified encoding scheme and return the value.

This rule could not be implemented as a unidirectional rule because the `csv` module would not know how to decode the bytes object.
