# MCP CSV Query

This is an exploratory and demonstration project that uses a Model Context Protocol (MCP) server to provide LLM access and Structured Query Language (SQL) support to query CSV data to improve LLM responses.

## Built With

* Ollama locally-hosted llama3.2 LLM
* [FastMCP v2 framework](https://github.com/jlowin/fastmcp)
* NFL player data from https://github.com/hvpkod/NFL-Data/blob/main/NFL-data-Players/2025/1/WR.csv

## Overview

MCP is a standardized way to expose tools to an LLM that can be used to access information and perform functions.  This project allows the LLM to provide SQL queries to the MCP server, which in turn executes those queries on a database created from the source CSV file.

The goal of this project is to ask the LLM a question related to NFL player performance (discussed below) and see if the responses improve if supporting data is provided to the LLM via MCP.  For each question, the following process was used:

* The correct answer is determined using manual methods
* The question is provided to the LLM with no supporting data (intended to validate that the LLM does not have the data and cannot answer the question properly)
* The question is provided to the same LLM but with RAG and a CSV file that contains the data needed to answer the question

Overall the LLM without RAG data was unable to answer the questions, but was able to with RAG data.

## Discussion

### CSV Data

The CSV data used is available [here](https://github.com/hvpkod/NFL-Data/blob/main/NFL-data-Players/2025/1/WR.csv).  This data is for week 1 of the 2025 NFL season.  Each row represents a single player with statistics about their performance in that week's game.

The relevant columns of data for the project question is as follows:

* PlayerName
* ReceivingYDS

It is important to note that the LLM needs to interpret several aspects from the question, e.g. relating a player to the PlayerName column and relating the number of receiving yards they made to the ReceivingYDS column.  While there are high-level samples of the types of SQL queries that can be provided, there is no specific indication to the LLM what each column means.  It is also important to note that there are several similar columns that could be misinterpreted, e.g. PassingTD, ReceivingRec, ReceivingTD, RetTD, FumTD, TouchReceptions, and others.

### Question

The question is:

***which NFL wide receiver had the most receiving yards in week 1 of the 2025 season?***

The answer can be manually determined by inspection, and the answer is Zay Flowers with 143 receiving yards.

Providing the question to the LLM without the MCP server tools, the response was as follows:

```
I don't have any information about the 2025 NFL season, as it has not yet occurred. I can only provide information up to my knowledge cutoff date of December 2023. If you're looking for information on the 2024 or previous seasons, I'd be happy to try and help.
```

This validates that the LLM was not trained on, and otherwise does not have access to the recent NFL player data.

Providing the same question to the same LLM with the RAG CSV data, the response was:

```
The NFL wide receiver with the most receiving yards in Week 1 of the 2025 season is Zay Flowers with 143.0 yards.
```

This is the correct answer.

This question is fairly straightforward for the LLM with MCP access to the CSV data to answer, as it requires simply looking up the data and determining the max value.

## Conclusion and future work

This was an interesting project that I think clearly demonstrates the capability of MCP to improve LLM responses.

* explore additional MCP capabilities (tools vs resources vs prompts)
* exploring an entire season of data and conduct more in-depth analysis
* develop guardrails and other methods of prohibiting the agent from executing dangerous SQL queries or acting outside the designed intent
* evaluate the performance and capability of different models and model sizes to see if there are minimum model characteristics needed to fully take advantage of MCP, or if other limitations or requirements exist
* explore variations of providing prompt/context explanations of the CSV data
