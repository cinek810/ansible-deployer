"""Yaml schemas for validation"""

SCHEMAS = {
    "acl": {
            "acl_lists": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": {
                        "name": {
                            "type": "string",
                            "required": True
                        },
                        "groups": {
                            "type": "list",
                            "schema": {
                                "type": "string",
                                "required": True
                            }
                        },
                        "infra": {
                            "type": "list",
                            "schema": {
                                "type": "dict",
                                "schema": {
                                    "name": {
                                        "type": "string",
                                        "required": True
                                    },
                                    "stages": {
                                        "type": "list",
                                        "required": True
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },

    "infra": {
            "infrastructures": {
                "type": "list",
                "required": True,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "name": {
                            "type": "string",
                            "required": True
                        },
                        "stages": {
                            "type": "list",
                            "required": True,
                            "schema": {
                                "type": "dict",
                                "schema": {
                                    "name": {
                                        "type": "string",
                                        "required": True
                                    },
                                    "inventory": {
                                        "type": "string",
                                        "required": True
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },

    "tasks": {
            "setup_hooks": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": {
                        "name": {
                            "type": "string",
                            "required": True
                        },
                        "module": {
                            "type": "string",
                            "required": True
                        },
                        "opts": {
                            "type": "dict",
                            "required": False
                        }
                    }
                }
            },
            "play_items": {
                "type": "list",
                "required": True,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "name": {
                            "type": "string",
                            "required": True
                        },
                        "file": {
                            "type": "string",
                            "required": True
                        },
                        "runner": {
                            "type": "string",
                            "required": False,
                            "allowed": [
                                "ansible-playbook",
                                "py.test"
                            ]
                        },
                        "skip": {
                            "type": "list",
                            "required": False,
                            "schema": {
                                "type": "dict",
                                "schema": {
                                    "infra": {
                                        "type": "string",
                                        "required": True
                                    },
                                    "stage": {
                                        "type": "string",
                                        "required": True
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "tasks": {
                "type": "list",
                "required": True,
                "schema": {
                    "type": "dict",
                    "required": True,
                    "schema": {
                        "name": {
                            "type": "string",
                            "required": True
                        },
                        "play_items": {
                            "type": "list",
                            "required": True,
                            "schema": {
                                "type": "string",
                                "required": True
                            }
                        },
                        "verify_items": {
                            "type": "list",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "required": True
                            }
                        },
                        "allowed_for": {
                            "type": "list",
                            "required": True,
                            "schema": {
                                "type": "dict",
                                "required": True,
                                "schema": {
                                    "acl_group": {
                                        "type": "string",
                                        "required": True
                                    },
                                    "commit": {
                                        "type": "list",
                                        "required": False,
                                        "schema": {
                                            "type": "string"
                                        }
                                    }
                                }
                            }
                        },
                        "allow_limit": {
                            "type": "boolean",
                            "required": False
                        },
                        "tags": {
                            "type": "list",
                            "required": False
                        }
                    }
                }
            }
        }
}
