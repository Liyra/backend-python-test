ALTER TABLE todos
  ADD completed INTEGER(1);

UPDATE todos
SET completed=0;