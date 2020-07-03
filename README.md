# LastLink
Keep the last link in a branching chain of documents.

## What is It?
In a document chain, the only way to find the documents newer than yours is a service which shares
the ID of the last document. This is that service.

## How does it work?
When you've created a new document on the chain, POST the ID of that document to make it the last
link. When you're reading from the document chain, GET the last link from the service.

## Installation and Operation
Lambda and AWS-SAM make your life easy. Just use aws-sam deploy to deploy the code.
