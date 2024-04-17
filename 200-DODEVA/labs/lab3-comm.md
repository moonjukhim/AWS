
```bash
# Java
aws dynamodb create-table ^
  --table-name Notes ^
  --attribute-definitions AttributeName=UserId,AttributeType=S AttributeName=NoteId,AttributeType=N ^
  --key-schema AttributeName=UserId,KeyType=HASH AttributeName=NoteId,KeyType=RANGE ^
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

aws dynamodb wait table-exists --table-name Notes

aws dynamodb describe-table --table-name Notes | findstr TableStatus
```
---

```java
//Create DynamoDB client
        AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard()
                .build();

        //Use the DynamoDB document API wrapper
        DynamoDB dynamoDB = new DynamoDB(client);
```

```java
//TODO 1
table.putItem(
               new Item()
               .withPrimaryKey("UserId", userId, "NoteId", noteId)
               .withString("Note", note)
                );
```

```bash
mvn -q exec:java -Dexec.mainClass="dev.labs.dynamodb.notesLoadData"
```

---

```java
//TODO 2
QuerySpec spec = new QuerySpec()
                .withProjectionExpression("NoteId, Note")
                .withKeyConditionExpression("UserId = :v_Id")
                .withValueMap(new ValueMap()
                        .withString(":v_Id", userId));
```

---

```java
//TODO 3
ItemCollection<QueryOutcome> items = table.query(spec);
```

```bash
mvn -q exec:java -Dexec.mainClass="dev.labs.dynamodb.notesQuery"
```

---

```java
//TODO 4
ScanSpec scanSpec = new ScanSpec()
                .withFilterExpression("contains (Note, :v_txt)")
                .withValueMap(new ValueMap().withString(":v_txt", searchText))
                .withProjectionExpression("UserId, NoteId, Note");
```

---

```java
//TODO 6
Iterator<Item> item = page.iterator();
```

```bash
mvn -q exec:java -Dexec.mainClass="dev.labs.dynamodb.notesScan"
```

---

```java
//TODO 7
UpdateItemSpec updateItemSpec = new UpdateItemSpec()
.withPrimaryKey("UserId", userId, "NoteId", noteId)
.withUpdateExpression("set #inc = :val1")
.withNameMap(new NameMap()
.with("#inc", "Is_Incomplete"))
.withValueMap(new ValueMap()
.withString(":val1", "Yes"))
.withReturnValues(ReturnValue.ALL_NEW);
```

```bash
mvn -q exec:java -Dexec.mainClass="dev.labs.dynamodb.notesUpdate"
```

---

```txt
Maximum item size in DynamoDB is 400 KB
```

```java
.withConditionExpression("Is_Incomplete = :v_old")
```

```java
// TODO 9
catch (ConditionalCheckFailedException e) {
            System.out.println("\nUPDATE#2 - REPEAT: Printing item after the conditional update for the item - \"" + userId + "\" and \"" + noteId + "\"  - FAILURE:");
            System.out.println("UpdateItem failed on item due to unmatching condition!");
            System.err.println(e.getMessage());
        }
```

```java
// TODO 10
//Allow update to the Notes item only if the note is incomplete - SUCCESS
        updateExistingAttributeConditionally(table, qUserId, qNoteId, newNote);

        //Allow update to the Notes item only if the note is incomplete - FAILURE
        updateExistingAttributeConditionally(table, qUserId, qNoteId, newNote);
```

```bash
mvn -q exec:java -Dexec.mainClass="dev.labs.dynamodb.notesUpdate"
```
