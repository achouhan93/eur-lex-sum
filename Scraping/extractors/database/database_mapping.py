def elastic_search_mapping():
    # """"""""""
    # Functionality: Creation of the mapping for the ElasticSearch or OpenSearch Index
    # 
    # For this project mapping is created from JSON using https://json-to-es-mapping.netlify.app/
    #
    # Signature of the function:
    #  Input: 
    #       No input is required for this function, as it is executed to create an object for mapping
    # 
    #  Output:
    #       es_mapping: Mapping setting for the ElasticSearch or OpenSearch Index
    # """""""""" 
    es_mapping = {
        "settings": {
            "number_of_shards":1,
            "number_of_replicas":0
        },
        "mappings": {
            "properties": {
                "bulgarian": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "spanish": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "czech": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "danish": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "german": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "estonian": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "greek": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "english": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "french": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "irish": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "croatian": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "italian": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "latvian": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "lithuanian": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "hungarian": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "maltese": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "dutch": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "polish": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "portuguese": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "romanian": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "slovak": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "slovenian": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "finnish": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "swedish": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    return es_mapping