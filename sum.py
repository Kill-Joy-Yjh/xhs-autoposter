import os

def smart_combine(prefix):
    import json
    def extract_poem_pairs_xhs(obj):
        # 小红书风格：每组诗文配对，带emoji、分割线、引导语
        pairs = []
        poems = obj.get("classic_poems", []) if isinstance(obj, dict) else []
        translations = obj.get("modern_translations", []) if isinstance(obj, dict) else []
        n = min(len(poems), len(translations))
        for i in range(n):
            poem = poems[i]
            trans = translations[i]
            author = poem.get("author", "")
            content = poem.get("content", "")
            dynasty = poem.get("dynasty", "")
            keywords = poem.get("keywords", [])
            title = poem.get("title", "")
            translation = trans.get("translation", "")
            kw_str = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)
            block = (
                f"---\n"
                f"📜 **{title}**\n"
                f"👤 作者：{author}   🏛️ 朝代：{dynasty}\n"
                f"🔑 关键词：{kw_str}\n\n"
                f"🌿 原文：\n{content}\n\n"
                f"💡 译文：\n{translation}\n\n"
                f"✨ 你喜欢这首诗吗？欢迎在评论区留言你的感受！\n"
            )
            pairs.append(block)
        return pairs

    fields = [
        ("title", "标题"),
        ("input", "输入"),
        ("output", "输出"),
        ("output1", "扩展输出"),
    ]
    result = []
    # 自动插入头图和尾图（data为头，data1为尾）
    # 头部图片
    for ext in (".jpg", ".png", ".jpeg", ".webp"):
        img_path = f"{prefix}_data{ext}"
        if os.path.exists(img_path):
            result.append(f"![头图]({img_path})\n")
            break
    # 标题单独加粗居中
    title_path = f"{prefix}_title.txt"
    if os.path.exists(title_path):
        with open(title_path, "r", encoding="utf-8") as f:
            title = f.read().strip()
        result.append(f"\n<p align='center'><b>{title}</b></p>\n")
    # 输入（如有）
    input_path = f"{prefix}_input.txt"
    if os.path.exists(input_path):
        with open(input_path, "r", encoding="utf-8") as f:
            input_text = f.read().strip().replace("\\n", "\n")
        result.append(f"\n> 💭 主题：{input_text}\n")
    # 输出和扩展输出
    for key in ("output", "output1"):
        json_fname = f"{prefix}_{key}.json"
        txt_fname = f"{prefix}_{key}.txt"
        if os.path.exists(json_fname):
            try:
                with open(json_fname, "r", encoding="utf-8") as f:
                    content = json.load(f)
                pairs = extract_poem_pairs_xhs(content)
                text_block = "\n".join(pairs)
                result.append(text_block)
            except Exception as e:
                result.append(f"(解析JSON失败)\n")
        elif os.path.exists(txt_fname):
            with open(txt_fname, "r", encoding="utf-8") as f:
                content = f.read().strip().replace("\\n", "\n")
            result.append(content)
    # 结尾引导语和尾图
    for ext in (".jpg", ".png", ".jpeg", ".webp"):
        img_path = f"{prefix}_data1{ext}"
        if os.path.exists(img_path):
            result.append(f"![尾图]({img_path})\n")
            break
    result.append("---\n❤️ 喜欢的话记得点赞+收藏+关注！#国学 #诗词 #美好生活\n")
    # 合并为 markdown
    md_content = "\n".join(result)
    outname = f"{prefix}_xhs.md"
    with open(outname, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"已生成小红书风格合并文件: {outname}")

if __name__ == "__main__":
    # 自动查找所有 coze_stream_raw_*_input.txt 文件，批量合并
    for fname in os.listdir('.'):
        if fname.startswith("coze_stream_raw_") and fname.endswith("_input.txt"):
            prefix = fname[:-10]  # 去掉 _input.txt
            smart_combine(prefix)