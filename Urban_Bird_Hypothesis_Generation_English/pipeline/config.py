import os

# ------------------------------------ API Configuration ------------------------------------
# Using Zhipu AI API as an example.
# Replace with your preferred model configuration.

# Free official Gemini API (slow)
# API_CONFIG = {
#     "config_name": "my_config",
#     "model_type": "openai_chat",
#     "model_name": "cdeepseek-r1",
#     "api_key": "YOUR_API_KEY",
#     "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
# }

# Official Zhipu AI API
# MODEL_CONFIG = {
#     "config_name": "my_config",
#     "model_type": "zhipuai_chat",
#     "model_name": "glm-4", # -airx
#     "api_key": "YOUR_API_KEY",  # Please replace with your API key
#     "base_url": "https://open.bigmodel.cn/api/paas/v4/",
# }

# API call via a third-party service (Usually used, Models are optional via "model_name")
# Expert_MODEL_CONFIG = {
#             "config_name": "Expert_config",
#         "model_type": "zhipuai_chat",
#         "model_name": "glm-4", # -airx
#         "api_key": "YOUR_API_KEY",  # Please replace with your API key
#         "base_url": "https://open.bigmodel.cn/api/paas/v4/",
#         }
#
# GrandExpert_MODEL_CONFIG = {
#             "config_name": "GrandExpert_config",
#     "model_type": "zhipuai_chat",
#     "model_name": "glm-4",  # -airx
#     "api_key": "YOUR_API_KEY",  # Please replace with your API key
#     "base_url": "https://open.bigmodel.cn/api/paas/v4/",
#         }
#
# Screener_MODEL_CONFIG = {
#             "config_name": "Screener_config",
#     "model_type": "zhipuai_chat",
#     "model_name": "glm-4",  # -airx
#     "api_key": "YOUR_API_KEY",  # Please replace with your API key
#     "base_url": "https://open.bigmodel.cn/api/paas/v4/",
#         }
#
# Critic_MODEL_CONFIG = {
#             "config_name": "Critic_config",
#     "model_type": "zhipuai_chat",
#     "model_name": "glm-4",  # -airx
#     "api_key": "YOUR_API_KEY",  # Please replace with your API key
#     "base_url": "https://open.bigmodel.cn/api/paas/v4/",
#         }

# gemini-3.1-pro-preview-thinking-thinking
# gemini-3.1-pro-preview-thinking-thinking
# gemini-3.1-pro-preview-thinking-thinking
# # API call via a third-party service (Usually used, Models are optional via "model_name")
Expert_MODEL_CONFIG = {
            "config_name": "Expert_config",
            "model_type": "openai_chat",
            "model_name": "gemini-3.1-pro-preview-thinking",
            "api_key": os.environ.get("LLM_API_KEY", ""),
            "client_args": {
                #"base_url": "https://svip.xty.app/v1",
                "base_url": "https://svip-ip.xty.app/v1",
                "timeout": 600
             },
            "generation_kwargs": {
                    "response_format": {
                        "type": "json_object"
                    }
                }
        }

GrandExpert_MODEL_CONFIG = {
            "config_name": "GrandExpert_config",
            "model_type": "openai_chat",
            "model_name": "gemini-3.1-pro-preview-thinking",
            "api_key": os.environ.get("LLM_API_KEY", ""),
            "client_args": {
                #"base_url": "https://svip.xty.app/v1",
                "base_url": "https://svip-ip.xty.app/v1",
                "timeout": 600
            },
            "generation_kwargs": {
                    "response_format": {
                        "type": "json_object"
                    }
                }
        }

Screener_MODEL_CONFIG = {
            "config_name": "Screener_config",
            "model_type": "openai_chat",
            "model_name": "gemini-3.1-pro-preview-thinking",
            "api_key": os.environ.get("LLM_API_KEY", ""),
            "client_args": {
                #"base_url": "https://svip.xty.app/v1",
                "base_url": "https://svip-ip.xty.app/v1",
                "timeout": 600
            },
            "generation_kwargs": {
                    "response_format": {
                        "type": "json_object"
                    }
                }
        }

Critic_MODEL_CONFIG = {
            "config_name": "Critic_config",
            "model_type": "openai_chat",
            "model_name": "gemini-3.1-pro-preview-thinking",
            "api_key": os.environ.get("LLM_API_KEY", ""),
            "client_args": {
                #"base_url": "https://svip.xty.app/v1",
                "base_url": "https://svip-ip.xty.app/v1",
                "timeout": 600
            },
            "generation_kwargs": {
                    "response_format": {
                        "type": "json_object"
                    }
                }
        }

# Another third-party service
# MODEL_CONFIG =   {
#             "config_name": "my_config",
#             "model_type": "openai_chat",
#             "model_name": "gemini-3.1-pro-preview-thinking-thinking",
#             "api_key": "YOUR_API_KEY",
#             "client_args": {
#                 "base_url": "https://www.chataiapi.com/v1",
#             },
#         }


CONFIG = {

    "paths": {
        "CLL_PATH": '../Corpus_of_species_interaction/bird1487/UrbanBirdDiversity_Corpus_1487.json'
    },

    # ------------------------------------ Document Processing Settings ------------------------------------
    "docs": {
        "INCLUDE_CONCLUSION_CONTENT": False, # Whether to include the conclusion; set to False.
        "INCLUDE_INTRO": False, # Whether to include the introduction; set to False.
        "MAX_INSPIRATIONS_WINDOW": 15,
        "MIN_INSPIRATIONS_WINDOW": 10,
        "SLIDING_WINDOW_SIZE": 15,
        "SCREENER_WINDOW_SIZE": 100,
        "INCLUDE_REASONING": False  # Whether to include reasoning when the inspiration pool is used as a prompt.
    },

    # ------------------------------------ Agent Definitions ------------------------------------
    "agents": {
        "PHASE1_EXPERT_SUBFIELDS": {
            "Dr_Expert": "Urban biodiversity",
        },
        "PHASE2_EXPERT_SUBFIELDS": {
            "Dr_Expert1": "Community ecology",
            "Dr_Expert2": "Population ecology",
            "Dr_Expert3": "Avian ecology",
            "Dr_Expert4": "Plant ecology",
            "Dr_Expert5": "Conservation biology",
            "Dr_Expert6": "Urban planning and design",
            "Dr_Expert7": "Social science"
        },

        "GRANDEXPERT_FIELD": "Urban ecology, specialized in urban biodiversity"
    },

    # ------------------------------------ Research Topic and Background ------------------------------------
    "research": {
        "RESEARCH_TOPIC": "Identify novel, important, yet underexplored factors and processes affecting urban bird diversity",
        "RESEARCH_BACKGROUND":"Historically, urban ecology and conservation biology have focused on elucidating the patterns of avian diversity and the multi-scale drivers that shape them. Within these novel ecosystems, bird communities are governed by a complex interplay between anthropogenic landscape modifications and biotic interactions—including both interspecific competition and multi-trophic dynamics. These forces collectively determine the taxonomic, functional, and phylogenetic facets of urban avian assemblages. However, the burgeoning volume of published research across disparate scales complicates the synthesis of existing knowledge, often obscuring underexplored ecological factors and processes that remain concealed within fragmented studies."
    },

    "Phase_2_config" : {
    "USE_API_FOR_NEW_PAPERS": True,
    "multiple_num_of_COP" : 3,
    "max_refinement_loops" : 1,
    "keyWords_num_papers" : 5, # If relevance retrieval fails, return keyWords_num_papers articles based directly on keywords.
    "iteration_GrandExpert_Critic" : 3,
    "max_rounds_discussion": 3,
    "chain_length" : 5,
    "chain_per_expert": 1,
    "num_chains_to_build": 7,
    "min_num_inspirations_discussion": 2,
    "max_num_inspirations_discussion": 3,
    "min_PoolSize_discussion":10,
    "max_PoolSize_discussion":30,
    "api_source" : 'semantic'
    },

    # Convenient for logging, but not used
    "Expert_MODEL_CONFIG": Expert_MODEL_CONFIG,
    "GrandExpert_MODEL_CONFIG": GrandExpert_MODEL_CONFIG,
    "Screener_MODEL_CONFIG": Screener_MODEL_CONFIG,
    "Critic_MODEL_CONFIG": Critic_MODEL_CONFIG
}

