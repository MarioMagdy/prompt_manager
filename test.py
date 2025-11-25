import prompt_manager_yml

pm = prompt_manager_yml.PromptManager("prompts", strict=True)


print(pm.list_prompts())
# ['email_verification', 'simple_prompt', 'welcome', ...]

text = pm.render(
    "welcome",
    name="Mario",
    app_name="Skill Navigator"
)
print(text)
# "Hello Mario, welcome to Skill Navigator!"
