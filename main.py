import gradio as gr
from config_tool import get_conf,get_free_port
import erniebot
API_TYPE, ACCESS_TOKEN, WEB_PORT, LLM_MODEL = get_conf('API_TYPE', 'ACCESS_TOKEN', 'WEB_PORT', 'LLM_MODEL')

# if WEB_PORT是-1, 则随机选取WEB端口
PORT = get_free_port() if WEB_PORT <= 0 else WEB_PORT
with gr.Blocks() as demo:
    with gr.Row().style(equal_height=True):
        with gr.Column(scale=3):
            chatbot = gr.Chatbot()
            chatbot.style(height=950)
            history = gr.State([])
        with gr.Column(scale=2):
            with gr.Row():
                msg = gr.Textbox(show_label=False, placeholder="输入内容.").style(container=False)
            with gr.Row():
                sub = gr.Button("提交", variant="primary")
            with gr.Row():
                clear = gr.Button("清除", variant="secondary")
                clear.style(size="sm")
            with gr.Row():
                status = gr.Markdown(
                    f"操作说明:\n 按Enter提交, 按Shift+Enter换行。\n当前模型: {LLM_MODEL} \n 功能区操作:输入内容点击相应功能区按钮即可出结果")
            with gr.Accordion("功能区", open=True) as basic_fn:
                with gr.Row():
                    bt1 = gr.Button("中文润色", variant="primary").style(size="sm")
                with gr.Row():
                    bt2 = gr.Button("英文润色", variant="primary").style(size="sm")
                with gr.Row():
                    bt3 = gr.Button("解释代码", variant="primary").style(size="sm")
                with gr.Row():
                    bt4 = gr.Button("中文错别字", variant="primary").style(size="sm")

    def user(user_message, history):
        return "", history + [[user_message, None]]

    def bot(history):
        print(history)
        if history[-1][0] is None or history[-1][0] == '':
            print('请输入内容！')
            return
        erniebot.api_type = API_TYPE
        erniebot.access_token = ACCESS_TOKEN
        response_ernie = erniebot.ChatCompletion.create(
            model=LLM_MODEL,
            messages=[{'role': 'user', 'content': history[-1][0]}],
            stream=True
        )
        history[-1][1] = ""
        for character in response_ernie:
            history[-1][1] += character.get_result()
            yield history


    def basic_in(user_message, history, type):
        return "", history + [[user_message, type]]

    def basic(history):
        print(history)
        position = 0
        if history[-1][1] == '英文润色':
            position = 1
        elif history[-1][1] == '解释代码':
            position = 2
        elif history[-1][1] == '中文错别字':
            position = 3
        prefix = ['作为一名中文学术论文写作助理，你的任务是改进所提供文本的拼写、语法、清晰、简洁明了和整体可读性，同时修改错别字，分解长句，减少重复。请只提供文本的更正版本，避免包括解释。请编辑以下文本。','Below is a paragraph from an academic paper. Polish the writing to meet the academic style,improve the spelling, grammar, clarity, concision and overall readability. When necessary, rewrite the whole sentence.Furthermore, list all modification and explain the reasons to do so in markdown table.','请解释以下代码：','请找出下面一段中文的错别字，并修改，禁止修改英文：']
        if history[-1][0] is None or history[-1][0] == '':
            print('请输入内容！')
            return
        erniebot.api_type = API_TYPE
        erniebot.access_token = ACCESS_TOKEN
        response_ernie = erniebot.ChatCompletion.create(
            model=LLM_MODEL,
            messages=[{'role': 'user', 'content': prefix[position]+history[-1][0]}],
            stream=True
        )
        history[-1][1] = ""
        for character in response_ernie:
            history[-1][1] += character.get_result()
            yield history
    # 回车提交
    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    sub.click(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    bt1.click(basic_in, [msg, chatbot,gr.State('中文润色')], [msg, chatbot], queue=False).then(
        basic, chatbot, chatbot
    )
    bt2.click(basic_in, [msg, chatbot, gr.State('英文润色')], [msg, chatbot], queue=False).then(
        basic, chatbot, chatbot
    )
    bt3.click(basic_in, [msg, chatbot, gr.State('解释代码')], [msg, chatbot], queue=False).then(
        basic, chatbot, chatbot
    )
    bt4.click(basic_in, [msg, chatbot, gr.State('中文错别字')], [msg, chatbot], queue=False).then(
        basic, chatbot, chatbot
    )

    clear.click(lambda: None, None, chatbot, queue=False)


demo.queue(concurrency_count=100)
demo.title = "ERNIE Bot学术应用"
demo.launch(server_port=PORT, share=False)
