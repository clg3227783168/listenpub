# -*- coding: utf-8 -*-
import json
import os
from typing import Dict, Any

class I18nHelper:
    def __init__(self):
        self.current_language = 'zh'
        self.translations = {}
        self.load_translations()

    def load_translations(self):
        """加载中文翻译文件"""
        locales_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'locales')
        lang_file = os.path.join(locales_dir, 'zh', 'messages.json')
        if os.path.exists(lang_file):
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.translations['zh'] = json.load(f)

    def set_language(self, language: str):
        """设置当前语言（固定为中文）"""
        self.current_language = 'zh'
        return True

    def get_language(self) -> str:
        """获取当前语言"""
        return self.current_language

    def t(self, key: str, **kwargs) -> str:
        """获取翻译文本"""
        if self.current_language not in self.translations:
            return key

        translation = self.translations[self.current_language].get(key, key)

        # 支持参数替换
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except KeyError:
                pass

        return translation


    def get_language_choices(self) -> list:
        """获取语言选择列表（仅中文）"""
        return ["中文"]

# 全局i18n实例
i18n = I18nHelper()