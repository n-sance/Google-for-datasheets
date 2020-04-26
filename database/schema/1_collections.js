db.createCollection("datasheets", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["id", "component_name", "filename", "access_groups", "versions"],
            properties: {
                id: {
                    bsonType: "int",
                    description: "Unique datasheet id"
                },
                component_name: {
                    bsonType: "string",
                    description: "Component name"
                },
                filename: {
                    bsonType: "string",
                    description: "Document filename"
                },
                access_groups: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        required: ["group_id", "mode"],
                        properties: {
                            group_id: {
                                bsonType: "int",
                                description: "Group id"
                            },
                            mode: {
                                enum: ["read-only", "read-and-write"],
                                description: "Access mode"
                            }
                        },
                    },
                    description: "Array of access groups"
                },
                versions: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        required: ["id", "creator_id", "date_created", "text", "datasheet_url"],
                        properties: {
                            id: {
                                bsonType: "int",
                                description: "Version id"
                            },
                            creator_id: {
                                bsonType: "int",
                                description: "Id of the user who created this version"
                            },
                            date_created: {
                                bsonType: "date",
                                description: "Date when this version was created"
                            },
                            datasheet_url: {
                                bsonType: "string",
                                description: "Url of the datasheet"
                            }
                        },
                    },
                    description: "Array of access groups"
                }
            }
        }
    }
})

db.createCollection("groups", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["id", "creator_id", "date_created", "members"],
            properties: {
                id: {
                    bsonType: "int",
                    description: "Group id"
                },
                creator_id: {
                    bsonType: "int",
                    description: "Id of the user who created the group"
                },
                date_created: {
                    bsonType: "date",
                    description: "Date when this group was created"
                },
                members: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        required: ["user_id", "role"],
                        properties: {
                            user_id: {
                                bsonType: "int",
                                description: "User id"
                            },
                            role: {
                                enum: ["viewer", "member", "administrator"],
                                description: "User role in the group"
                            }
                        },
                    },
                    description: "Array of group members"
                }
            }
        }
    }
})
