package com.example.resultsapp

data class ResultItem(
    val year: String,
    val number: String,
    val name: String,
    val fields: Map<String, String> = emptyMap()
)

data class ResultsFile(
    val count: Int,
    val results: List<ResultItem>
)
