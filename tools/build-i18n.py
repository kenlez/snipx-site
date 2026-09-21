#!/usr/bin/env python3
"""SnipX-site i18n 生成器。

用法：
    python3 tools/build-i18n.py

从内嵌的中文模板 + 翻译字典，生成 7 个语种 × 3 个页面 = 21 个 HTML
文件，加上 3 个根 / 路径自动跳转文件。所有产出位于：
    <lang>/index.html / privacy.html / support.html
    /index.html / privacy.html / support.html  （语言选择 / 跳转）

设计要点：
- 静态站点无构建步骤：本脚本是维护工具，不在运行时被调用
- 翻译字典缺失字段回退 zh-CN（首次生成后再人工翻译）
- 所有 assets/ 资源引用改为根相对路径（/assets/...），便于子目录访问
- 同一页面的语种切换由 assets/js/i18n.js 处理（保留当前页面）
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent

LANGS = ["zh-CN", "zh-TW", "en", "ja", "ko", "es", "pt"]
PAGES = ["index", "privacy", "support"]

# ---------------------------------------------------------------------------
# 翻译字典（zh-CN 为源，缺字段回退；非中文/英语标记机译供手测）
# 添加新字符串：先在 zh-CN 模板里写好中文，再在每个语种里加对应译文。
# ---------------------------------------------------------------------------

T = {
    "zh-CN": {},  # 源语言，未翻译

    "zh-TW": {
        # 通用
        "下载 SnipX": "下載 SnipX",
        "主题：跟随系统": "主題：跟隨系統",
        "主题：浅色": "主題：淺色",
        "主题：深色": "主題：深色",
        "特性": "特色",
        "下载": "下載",
        "关于": "關於",
        "查看功能": "查看功能",
        "主页": "首頁",
        "支持": "支援",
        "隐私政策": "隱私政策",
        "© 2026 SnipX. All rights reserved.": "© 2026 SnipX. All rights reserved.",
        # hero
        "macOS 14+ · 原生应用": "macOS 14+ · 原生應用",
        "Mac 截屏与录屏，一触即达。": "Mac 截圖與錄螢，一觸即達。",
        "原生 AppKit + Swift + ScreenCaptureKit。物理像素输出、本地 OCR、可编辑快捷键、长截图拼接、本地 MP4 录制。内容在本机处理，无需注册 SnipX 账号。":
            "原生 AppKit + Swift + ScreenCaptureKit。物理像素輸出、本地 OCR、可編輯快捷鍵、長截圖拼接、本地 MP4 錄製。內容在本機處理，無需註冊 SnipX 帳號。",
        "macOS 14+": "macOS 14+",
        "Universal 2 · Apple Silicon + Intel": "Universal 2 · Apple Silicon + Intel",
        "本地 OCR": "本地 OCR",
        "SnipX Pro 录屏/GIF": "SnipX Pro 錄螢/GIF",
        "下载 SnipX": "下載 SnipX",
        # features
        "菜单栏常驻，所见即可截": "選單列常駐，所見即可截",
        "截屏、标注、录屏、长截图，全部在菜单栏一触即达。": "截圖、標註、錄螢、長截圖，全部在選單列一觸即達。",
        "常驻菜单栏": "常駐選單列",
        "点击即开，不打扰": "點擊即開，不打擾",
        "SnipX 始终浮于屏幕角落的菜单栏。无需打开主窗口，点击即弹出截屏 / 录屏入口。":
            "SnipX 始終浮於螢幕角落的選單列。無需打開主視窗，點擊即彈出截圖 / 錄螢入口。",
        "截屏、录屏、标注、设置 全部直达": "截圖、錄螢、標註、設定 全部直達",
        "不抢焦点、不打扰当前工作": "不搶焦點、不打擾目前工作",
        "原生菜单栏图标，遵循 macOS 设计语言": "原生選單列圖示，遵循 macOS 設計語言",
        "可编辑快捷键": "可編輯快捷鍵",
        "全局快捷键，自由绑定": "全域快捷鍵，自由綁定",
        "截屏、录屏、标注、长截图 — 每个动作都可绑定独立快捷键，避免与其他应用冲突。":
            "截圖、錄螢、標註、長截圖 — 每個動作都可綁定獨立快捷鍵，避免與其他應用程式衝突。",
        "支持单键 / 组合键 / 修饰键": "支援單鍵 / 組合鍵 / 修改鍵",
        "冲突检测，一键恢复默认": "衝突偵測，一鍵恢復預設",
        "录屏、截屏独立绑定，标注即时唤起": "錄螢、截圖獨立綁定，標註即時喚起",
        "四类截屏": "四類截圖",
        "区域 / 窗口 / 全屏 / 长截图": "區域 / 視窗 / 全螢幕 / 長截圖",
        "物理像素输出，自动按显示器倍率渲染。窗口截屏自动识别应用窗口边缘，长截图无缝拼接。":
            "物理像素輸出，自動依顯示器倍率渲染。視窗截圖自動辨識應用程式視窗邊緣，長截圖無縫拼接。",
        "区域截屏：拖拽选区，物理像素精度": "區域截圖：拖曳選取區，物理像素精度",
        "窗口截屏：自动选窗，背景透明": "視窗截圖：自動選窗，背景透明",
        "全屏截屏：多显示器同时输出": "全螢幕截圖：多顯示器同時輸出",
        "长截图：滚动拼接，自动对齐": "長截圖：捲動拼接，自動對齊",
        "本地 OCR（1.0.0 新增）": "本地 OCR（1.0.0 新增）",
        "截图里的文字，一键识别": "截圖裡的文字，一鍵辨識",
        "基于 Apple Vision 框架，在你的 Mac 上直接识别截图中的中文、英文与中英混合文本。识别结果可编辑、可复制，不上传任何内容。":
            "基於 Apple Vision 框架，在你的 Mac 上直接辨識截圖中的中文、英文與中英混合文字。辨識結果可編輯、可複製，不上傳任何內容。",
        "中文（简/繁）、英文与中英混排": "中文（簡/繁）、英文與中英混排",
        "完全本地识别，截图与文字不出本机": "完全本地辨識，截圖與文字不出本機",
        "识别后可编辑、复制或取消": "辨識後可編輯、複製或取消",
        "适用于截屏后的二次编辑与提取": "適用於截圖後的二次編輯與擷取",
        "标注工具": "標註工具",
        "矩形 / 箭头 / 文字 / 马赛克": "矩形 / 箭頭 / 文字 / 馬賽克",
        "截屏后即时标注，所有元素可移动、可删除、可撤销重做。裁剪、马赛克、颜色选择器一应俱全。":
            "截圖後即時標註，所有元素可移動、可刪除、可復原重做。裁剪、馬賽克、顏色選擇器一應俱全。",
        "矩形、椭圆、箭头、画笔、文字": "矩形、橢圓、箭頭、畫筆、文字",
        "马赛克模糊敏感信息": "馬賽克模糊敏感資訊",
        "撤销 / 重做 / 裁剪 / 颜色选择器": "復原 / 重做 / 裁剪 / 顏色選擇器",
        "本地 MP4 录屏 · SnipX Pro": "本地 MP4 錄螢 · SnipX Pro",
        "倒计时 · 系统声 + 麦克风 · 自动恢复": "倒數計時 · 系統聲 + 麥克風 · 自動復原",
        "基于 ScreenCaptureKit 本地录制，支持同时录制系统声音与麦克风，倒计时、磁盘保护、异常恢复一应俱全。头尾裁剪导出，无需第三方编辑器。":
            "基於 ScreenCaptureKit 本地錄製，支援同時錄製系統聲音與麥克風，倒數計時、磁碟保護、異常復原一應俱全。頭尾裁剪匯出，無需第三方編輯器。",
        "区域 / 窗口 / 显示器三种录屏模式": "區域 / 視窗 / 顯示器三種錄螢模式",
        "系统声音与麦克风同时录制，单一音轨": "系統聲音與麥克風同時錄製，單一音軌",
        "倒计时与状态指示，录屏不打断": "倒數計時與狀態指示，錄螢不打斷",
        "异常退出后 Recovery 保留录制": "異常退出後 Recovery 保留錄製",
        "头尾裁剪导出为新 MP4": "頭尾裁剪匯出為新 MP4",
        "录屏与 GIF 录制需解锁 <strong>SnipX Pro</strong>（一次性买断，价格以 App Store 为准）。截屏、标注、长截图永久免费。":
            "錄螢與 GIF 錄製需解鎖 <strong>SnipX Pro</strong>（一次性買斷，價格以 App Store 為準）。截圖、標註、長截圖永久免費。",
        "零数据外传": "零資料外傳",
        "完全离线运行": "完全離線運作",
        "截图、录屏与 OCR 在本机处理，不自动上传内容或遥测。购买与恢复通过 Apple 服务完成。":
            "截圖、錄螢與 OCR 在本機處理，不自動上傳內容或遙測。購買與復原透過 Apple 服務完成。",
        "购买与恢复可能需要联网": "購買與復原可能需要連線",
        "无账号、无登录、无云同步": "無帳號、無登入、無雲端同步",
        "无第三方 SDK、无埋点": "無第三方 SDK、無埋點",
        "开源友好的本地存储": "開源友善的本機儲存",
        # install
        "从 Mac App Store 获取": "從 Mac App Store 取得",
        "在 App Store 一键安装，内购、更新与恢复购买由 Apple 处理。":
            "在 App Store 一鍵安裝，內購、更新與復原購買由 Apple 處理。",
        "前往 App Store": "前往 App Store",
        "点击下方按钮，跳转 Mac App Store 的 SnipX 应用页。": "點擊下方按鈕，跳轉 Mac App Store 的 SnipX 應用程式頁。",
        "安装并打开": "安裝並開啟",
        "点按「获取」安装 SnipX，完成后从「应用程序」或菜单栏打开。":
            "點按「取得」安裝 SnipX，完成後從「應用程式」或選單列開啟。",
        "授权系统权限": "授權系統權限",
        "按所用功能授权：屏幕录制、系统声音、麦克风和摄像头。":
            "按所用功能授權：螢幕錄製、系統聲音、麥克風和攝影機。",
        "前往 App Store 下载": "前往 App Store 下載",
        "App Store 应用页即将上线，链接待回填。": "App Store 應用程式頁即將上線，連結待回填。",
        "macOS 14+ · Universal 2（Apple Silicon + Intel）· 仅 3 MB":
            "macOS 14+ · Universal 2（Apple Silicon + Intel）· 僅 3 MB",
        "基础截屏永久免费 · 录屏与 GIF 录制需 <a href=\"./#about\">SnipX Pro</a>（一次性买断）":
            "基礎截圖永久免費 · 錄螢與 GIF 錄製需 <a href=\"./#about\">SnipX Pro</a>（一次性買斷）",
        # about
        "关于 SnipX": "關於 SnipX",
        "原生开发": "原生開發",
        "Swift + AppKit + SwiftUI + ScreenCaptureKit + AVFoundation + Carbon 编写，无 WebView、无 Electron、无包装层。":
            "Swift + AppKit + SwiftUI + ScreenCaptureKit + AVFoundation + Carbon 編寫，無 WebView、無 Electron、無包裝層。",
        "隐私优先": "隱私優先",
        "内容处理在本机，无需注册 SnipX 账号。购买由 Apple 处理；主动分享由你选择。详见":
            "內容處理在本機，無需註冊 SnipX 帳號。購買由 Apple 處理；主動分享由你選擇。詳見",
        "SnipX Pro": "SnipX Pro",
        "截屏、标注、长截图、置顶永久免费。一次性买断解锁 MP4 录屏与 GIF 录制，价格以 App Store 为准。":
            "截圖、標註、長截圖、置頂永久免費。一次性買斷解鎖 MP4 錄螢與 GIF 錄製，價格以 App Store 為準。",
        "持续维护": "持續維護",
        "当前版本": "目前版本",
        "每个版本均经过手测、单元测试、功能测试三道关。需要帮助？":
            "每個版本均經過手測、單元測試、功能測試三道關。需要幫助？",
        "支持页": "支援頁",
        # footer
        "当前版本 1.0.0": "目前版本 1.0.0",
        # images alt
        "SnipX 界面预览": "SnipX 介面預覽",
        "SnipX 菜单栏截屏入口": "SnipX 選單列截圖入口",
        "SnipX 全局快捷键设置": "SnipX 全域快捷鍵設定",
        "SnipX 区域 / 窗口 / 全屏 / 长截图": "SnipX 區域 / 視窗 / 全螢幕 / 長截圖",
        "SnipX 本地 OCR 识别截图文字": "SnipX 本地 OCR 辨識截圖文字",
        "SnipX 标注工具": "SnipX 標註工具",
        "SnipX MP4 录屏": "SnipX MP4 錄螢",
        "SnipX 完全离线运行": "SnipX 完全離線運作",
        # privacy
        "Privacy Policy": "Privacy Policy",
        "SnipX 隐私政策": "SnipX 隱私政策",
        "最后更新：2026 年 9 月 6 日 · 适用于 SnipX macOS 应用与本站": "最後更新：2026 年 9 月 6 日 · 適用於 SnipX macOS 應用程式與本站",
        "内容在本机处理": "內容在本機處理",
        "截图、录屏、声音、摄像头画面、OCR 识别结果和标注均在你的 Mac 上处理。SnipX 不会自动把这些内容或本地诊断日志上传给开发者，不集成广告、追踪或第三方分析 SDK。":
            "截圖、錄螢、聲音、攝影機畫面、OCR 辨識結果和標註均在你的 Mac 上處理。SnipX 不會自動把這些內容或本地診斷記錄上傳給開發者，不整合廣告、追蹤或第三方分析 SDK。",
        "当你主动使用系统分享、发送反馈或将文件保存到云盘同步目录时，内容会按你的操作交给相应服务，其处理方式适用该服务的隐私政策。":
            "當你主動使用系統分享、傳送回饋或將檔案儲存到雲端同步目錄時，內容會按你的操作交給相應服務，其處理方式適用該服務的隱私政策。",
        "1. 系统权限": "1. 系統權限",
        "屏幕录制：": "螢幕錄製：",
        "用于截屏、长截图与录屏。": "用於截圖、長截圖與錄螢。",
        "系统声音：": "系統聲音：",
        "在你启用电脑声音录制时写入本地视频。": "在你啟用電腦聲音錄製時寫入本地影片。",
        "麦克风：": "麥克風：",
        "在你开启麦克风录制时申请，用于录制声音。": "在你開啟麥克風錄製時申請，用於錄製聲音。",
        "摄像头：": "攝影機：",
        "在你开启摄像头画面时申请，用于画中画。": "在你開啟攝影機畫面時申請，用於子母畫面。",
        "你可以在 macOS「系统设置 → 隐私与安全性」中管理权限。拒绝或撤销权限会影响对应功能。全局快捷键不要求额外开启辅助功能；在 Finder 中显示文件不要求自动化权限。":
            "你可以在 macOS「系統設定 → 隱私與安全性」中管理權限。拒絕或撤銷權限會影響對應功能。全域快捷鍵不要求額外開啟輔助功能；在 Finder 中顯示檔案不要求自動化權限。",
        "2. 文件、设置与本地日志": "2. 檔案、設定與本地記錄",
        "截图与录屏通过保存对话框导出到你选择的位置。录屏过程文件保存在应用支持目录的 SnipX/Recovery 中；本地诊断日志保存在 Library/Logs/SnipX/CrashLogs 中。沙盒版的这些应用目录位于 macOS 为 SnipX 分配的容器内，开发测试版也可能使用项目旁的 CrashLogs 目录。":
            "截圖與錄螢透過儲存對話框匯出到你選擇的位置。錄螢過程檔案儲存在應用支援目錄的 SnipX/Recovery 中；本地診斷記錄儲存在 Library/Logs/SnipX/CrashLogs 中。沙盒版的這些應用目錄位於 macOS 為 SnipX 分配的容器內，開發測試版也可能使用專案旁的 CrashLogs 目錄。",
        "应用在本机保存快捷键等偏好设置，并检查可用磁盘空间以保护录制文件。这些信息不会自动发送给开发者。OCR 使用 Apple Vision 框架在本机完成，不向服务器上传图片或识别结果。":
            "應用程式在本機儲存快捷鍵等偏好設定，並檢查可用磁碟空間以保護錄製檔案。這些資訊不會自動傳送給開發者。OCR 使用 Apple Vision 框架在本機完成，不向伺服器上傳圖片或辨識結果。",
        "删除应用本身不保证删除已导出文件、恢复文件和日志。请先保存需要保留的内容，再自行清理不需要的文件；不要在录制过程中删除恢复文件。":
            "刪除應用程式本身不保證刪除已匯出檔案、復原檔案和記錄。請先儲存需要保留的內容，再自行清理不需要的檔案；不要在錄製過程中刪除復原檔案。",
        "3. 购买与恢复购买": "3. 購買與復原購買",
        "SnipX Pro 为一次性买断的非消耗型内购，价格以 App 内和 Apple 购买确认界面为准。商品加载、购买、恢复及交易状态同步通过 Apple StoreKit 服务完成，可能需要联网。":
            "SnipX Pro 為一次性買斷的非消耗型內購，價格以 App 內和 Apple 購買確認介面為準。商品載入、購買、復原及交易狀態同步透過 Apple StoreKit 服務完成，可能需要連線。",
        "Apple 处理付款。SnipX 在本机验证 Apple 提供的交易及权益信息，以决定是否解锁录屏和 GIF。开发者不通过应用收集你的银行卡或支付账户信息。Apple 对其处理的信息适用":
            "Apple 處理付款。SnipX 在本機驗證 Apple 提供的交易及權益資訊，以決定是否解鎖錄螢和 GIF。開發者不透過應用程式收集你的銀行卡或支付帳戶資訊。Apple 對其處理的資訊適用",
        "Apple 隐私政策": "Apple 隱私政策",
        "4. 主动联系支持与访问官网": "4. 主動聯絡支援與瀏覽官網",
        "你主动发送邮件时，我们会收到你提供的邮箱、问题描述及附件，仅用于回复和排查问题。请勿发送无关的个人信息、密码或敏感截图；可以联系下方邮箱请求删除你提供的反馈材料。":
            "你主動傳送郵件時，我們會收到你提供的電子郵件、問題描述及附件，僅用於回覆和排查問題。請勿傳送無關的個人資訊、密碼或敏感截圖；可以聯絡下方電子郵件請求刪除你提供的回饋材料。",
        "本站没有加入广告或分析 SDK。网站托管服务可能处理提供页面和保障服务所需的 IP 地址、浏览器请求及访问日志；这与应用在本机处理截图的行为不同。":
            "本站沒有加入廣告或分析 SDK。網站託管服務可能處理提供頁面和保障服務所需的 IP 位址、瀏覽器請求及瀏覽記錄；這與應用程式在本機處理截圖的行為不同。",
        "5. 政策变更与联系方式": "5. 政策變更與聯絡方式",
        "隐私处理方式变化时，我们会更新本页面及更新日期。隐私问题或删除反馈材料的请求请联系":
            "隱私處理方式變化時，我們會更新本頁面及更新日期。隱私問題或刪除回饋材料的請求請聯絡",
        "使用说明见": "使用說明見",
        "支持与帮助": "支援與說明",
        # support
        "Support": "Support",
        "SnipX 支持与帮助": "SnipX 支援與說明",
        "FAQ、权限引导、反馈渠道 · 适用于 SnipX 1.0.0 及以上版本":
            "FAQ、權限引導、回饋渠道 · 適用於 SnipX 1.0.0 及以上版本",
        "系统要求": "系統需求",
        "macOS 14.0 Sonoma 或更高版本": "macOS 14.0 Sonoma 或更高版本",
        "支持 Apple Silicon（M1 / M2 / M3 / M4）与 Intel Mac": "支援 Apple Silicon（M1 / M2 / M3 / M4）與 Intel Mac",
        "通用构建（Universal 2）同时包含": "通用建置（Universal 2）同時包含",
        "截图、录屏与 OCR 在本机处理；商品加载、购买与恢复可能需要联网。":
            "截圖、錄螢與 OCR 在本機處理；商品載入、購買與復原可能需要連線。",
        "首次启动：权限引导": "首次啟動：權限引導",
        "SnipX 只会在你实际使用对应功能时申请系统权限，遵循 macOS 默认流程，不会启动即弹窗。":
            "SnipX 只會在你實際使用對應功能時申請系統權限，遵循 macOS 預設流程，不會啟動即彈跳視窗。",
        "首次截屏或录屏时系统会弹窗。授权后到「系统设置 → 隐私与安全性 → 屏幕录制」可看到 SnipX。":
            "首次截圖或錄螢時系統會彈跳視窗。授權後到「系統設定 → 隱私與安全性 → 螢幕錄製」可看到 SnipX。",
        "仅在你开启「录制麦克风」开关时申请。": "僅在你開啟「錄製麥克風」開關時申請。",
        "仅在你开启「录制摄像头」开关时申请。": "僅在你開啟「錄製攝影機」開關時申請。",
        "录制电脑声音时，按 macOS 的屏幕与系统音频录制权限提示操作。":
            "錄製電腦聲音時，按 macOS 的螢幕與系統音訊錄製權限提示操作。",
        "如果误点了「拒绝」，可以到「系统设置 → 隐私与安全性」手动开启；SnipX 内置的「权限」面板也会引导你跳转到对应位置。":
            "如果誤點了「拒絕」，可以到「系統設定 → 隱私與安全性」手動開啟；SnipX 內建的「權限」面板也會引導你跳轉到對應位置。",
        "Q1：SnipX 联网吗？会上传我的截图吗？": "Q1：SnipX 連線嗎？會上傳我的截圖嗎？",
        "截图、录屏、OCR 与标注在本机处理，不会自动上传给开发者。购买与恢复通过 Apple 服务完成，可能需要联网；主动分享或发邮件时，内容按你的操作交给相应服务。":
            "截圖、錄螢、OCR 與標註在本機處理，不會自動上傳給開發者。購買與復原透過 Apple 服務完成，可能需要連線；主動分享或發郵件時，內容按你的操作交給相應服務。",
        "Q2：SnipX Pro 是什么？哪些功能需要付费？": "Q2：SnipX Pro 是什麼？哪些功能需要付費？",
        "截屏、标注、长截图、置顶、复制、保存、分享等基础功能永久免费。": " 一鍵永久免費。",
        "（一次性买断，价格以 Apple 购买界面为准）": "（一次性買斷，價格以 Apple 購買介面為準）",
        "解锁：": "解鎖：",
        "MP4 录屏（选定区域 / 显示器）": "MP4 錄螢（選定區域 / 顯示器）",
        "GIF 录制": "GIF 錄製",
        "系统声音 + 麦克风同时录制": "系統聲音 + 麥克風同時錄製",
        "摄像头画中画": "攝影機子母畫面",
        "倒计时与异常自动恢复": "倒數計時與異常自動復原",
        "头尾裁剪导出": "頭尾裁剪匯出",
        "Q3：如何恢复购买？": "Q3：如何復原購買？",
        "打开 SnipX → 菜单栏 → 设置 → 录屏 → 付费墙卡底部「恢复购买」按钮。App 会通过 StoreKit 2 重新校验你的购买状态。":
            "開啟 SnipX → 選單列 → 設定 → 錄螢 → 付費牆卡片底部「復原購買」按鈕。App 會透過 StoreKit 2 重新驗證你的購買狀態。",
        "Q4：可以更换已授权的功能吗？": "Q4：可以更換已授權的功能嗎？",
        "截屏、标注、长截图的快捷键都可以在「设置 → 快捷键」中自定义，冲突时会自动提示。":
            "截圖、標註、長截圖的快捷鍵都可以在「設定 → 快捷鍵」中自訂，衝突時會自動提示。",
        "Q5：为什么我截不到 SnipX 自己的窗口？": "Q5：為什麼我截不到 SnipX 自己的視窗？",
        "SnipX 在录屏与截屏时会自动排除自身的菜单栏蒙层、操作浮层与录屏浮动条，避免污染画面。其他 SnipX 窗口（如设置、编辑录屏）默认会被正常捕获。":
            "SnipX 在錄螢與截圖時會自動排除自身的選單列蒙層、操作浮層與錄螢浮動條，避免污染畫面。其他 SnipX 視窗（如設定、編輯錄螢）預設會被正常擷取。",
        "Q6：OCR 支持哪些语言？": "Q6：OCR 支援哪些語言？",
        "1.0.0 起，OCR 支持中文（简/繁）、英文及中英混合文本，由 Apple Vision 框架在本地完成识别，无网络依赖。":
            "1.0.0 起，OCR 支援中文（簡/繁）、英文及中英混合文字，由 Apple Vision 框架在本地完成識別、無網路依賴。",
        "Q7：录屏文件保存在哪里？": "Q7：錄螢檔案儲存在哪裡？",
        "通过保存对话框导出到你选择的位置。录制过程文件保存在应用支持目录的 SnipX/Recovery 中，沙盒版位于 SnipX 的 macOS 容器内。应用会保留可恢复文件；退出前请先保存需要的内容。":
            "透過儲存對話框匯出到你選擇的位置。錄製過程檔案儲存在應用支援目錄的 SnipX/Recovery 中，沙盒版位於 SnipX 的 macOS 容器內。應用程式會保留可復原檔案；退出前請先儲存需要的內容。",
        "反馈与问题上报": "回饋與問題回報",
        "如果你遇到 bug、有功能建议或希望贡献想法：": "如果你遇到 bug、有功能建議或希望貢獻想法：",
        "邮箱：": "電子郵件：",
        "请附上：macOS 版本、SnipX 版本、复现步骤、必要时附截图或录屏":
            "請附上：macOS 版本、SnipX 版本、重現步驟、必要時附截圖或錄螢",
        "SnipX 在异常退出时会保留崩溃日志到": "SnipX 在異常退出時會保留當機記錄到",
        "提交问题时一并附上可大幅加快定位": "提交問題時一併附上可大幅加快定位",
        "版本与更新": "版本與更新",
        "当前最新版本：": "目前最新版本：",
        "完整版本变更说明见": "完整版本變更說明見",
        "相关链接": "相關連結",
        "产品主页": "產品首頁",
    },

    "en": {
        # common
        "下载 SnipX": "Download SnipX",
        "主题：跟随系统": "Theme: follow system",
        "主题：浅色": "Theme: light",
        "主题：深色": "Theme: dark",
        "特性": "Features",
        "下载": "Download",
        "关于": "About",
        "查看功能": "See features",
        "主页": "Home",
        "支持": "Support",
        "隐私政策": "Privacy Policy",
        "© 2026 SnipX. All rights reserved.": "© 2026 SnipX. All rights reserved.",
        # hero
        "macOS 14+ · 原生应用": "macOS 14+ · Native app",
        "Mac 截屏与录屏，一触即达。": "Mac screenshot & recording, one tap away.",
        "原生 AppKit + Swift + ScreenCaptureKit。物理像素输出、本地 OCR、可编辑快捷键、长截图拼接、本地 MP4 录制。内容在本机处理，无需注册 SnipX 账号。":
            "Native AppKit + Swift + ScreenCaptureKit. Pixel-perfect output, on-device OCR, editable shortcuts, scrolling capture, local MP4 recording. Everything stays on your Mac — no SnipX account required.",
        "macOS 14+": "macOS 14+",
        "Universal 2 · Apple Silicon + Intel": "Universal 2 · Apple Silicon + Intel",
        "本地 OCR": "On-device OCR",
        "SnipX Pro 录屏/GIF": "SnipX Pro recording/GIF",
        "下载 SnipX": "Download SnipX",
        # features
        "菜单栏常驻，所见即可截": "Always there in the menu bar",
        "截屏、标注、录屏、长截图，全部在菜单栏一触即达。": "Capture, annotate, record, and scroll-capture — all from the menu bar in one tap.",
        "常驻菜单栏": "Lives in the menu bar",
        "点击即开，不打扰": "Click to open, never in the way",
        "SnipX 始终浮于屏幕角落的菜单栏。无需打开主窗口，点击即弹出截屏 / 录屏入口。":
            "SnipX lives quietly in the corner of your menu bar. No main window to open — a single click reveals the capture / recording entry points.",
        "截屏、录屏、标注、设置 全部直达": "Capture, recording, annotation, settings — one tap each",
        "不抢焦点、不打扰当前工作": "Never steals focus or breaks your flow",
        "原生菜单栏图标，遵循 macOS 设计语言": "Native menu bar icon that follows macOS design",
        "可编辑快捷键": "Editable shortcuts",
        "全局快捷键，自由绑定": "Global shortcuts, freely assigned",
        "截屏、录屏、标注、长截图 — 每个动作都可绑定独立快捷键，避免与其他应用冲突。":
            "Capture, recording, annotation, scroll-capture — each action gets its own shortcut, with warnings before any conflict.",
        "支持单键 / 组合键 / 修饰键": "Single keys / combos / modifiers",
        "冲突检测，一键恢复默认": "Conflict detection, one-click reset",
        "录屏、截屏独立绑定，标注即时唤起": "Independent shortcuts for record & capture, annotation on demand",
        "四类截屏": "Four capture modes",
        "区域 / 窗口 / 全屏 / 长截图": "Region / window / full screen / scrolling",
        "物理像素输出，自动按显示器倍率渲染。窗口截屏自动识别应用窗口边缘，长截图无缝拼接。":
            "Pixel-perfect output, automatically rendered at your display scale. Window capture auto-detects app window edges; scrolling capture stitches seamlessly.",
        "区域截屏：拖拽选区，物理像素精度": "Region: drag to select, pixel-accurate",
        "窗口截屏：自动选窗，背景透明": "Window: auto-detect, transparent background",
        "全屏截屏：多显示器同时输出": "Full screen: multi-display at once",
        "长截图：滚动拼接，自动对齐": "Scrolling: auto-stitched, no seams",
        "本地 OCR（1.0.0 新增）": "On-device OCR (new in 1.0.0)",
        "截图里的文字，一键识别": "One-tap text recognition from your captures",
        "基于 Apple Vision 框架，在你的 Mac 上直接识别截图中的中文、英文与中英混合文本。识别结果可编辑、可复制，不上传任何内容。":
            "Powered by the Apple Vision framework, SnipX recognizes Chinese, English, and mixed Chinese/English text directly on your Mac. Edit or copy the result — nothing is uploaded.",
        "中文（简/繁）、英文与中英混排": "Simplified & Traditional Chinese, English, and mixed",
        "完全本地识别，截图与文字不出本机": "Fully on-device, never leaves your Mac",
        "识别后可编辑、复制或取消": "Edit, copy, or cancel after recognition",
        "适用于截屏后的二次编辑与提取": "Great for extracting text from captures",
        "标注工具": "Annotation tools",
        "矩形 / 箭头 / 文字 / 马赛克": "Rectangle / arrow / text / mosaic",
        "截屏后即时标注，所有元素可移动、可删除、可撤销重做。裁剪、马赛克、颜色选择器一应俱全。":
            "Annotate the moment you capture. Move, delete, undo, redo anything. Crop, mosaic, and a color picker — all built in.",
        "矩形、椭圆、箭头、画笔、文字": "Rectangle, ellipse, arrow, pen, text",
        "马赛克模糊敏感信息": "Mosaic sensitive details",
        "撤销 / 重做 / 裁剪 / 颜色选择器": "Undo / redo / crop / color picker",
        "本地 MP4 录屏 · SnipX Pro": "Local MP4 recording · SnipX Pro",
        "倒计时 · 系统声 + 麦克风 · 自动恢复": "Countdown · system audio + mic · auto-recovery",
        "基于 ScreenCaptureKit 本地录制，支持同时录制系统声音与麦克风，倒计时、磁盘保护、异常恢复一应俱全。头尾裁剪导出，无需第三方编辑器。":
            "Built on ScreenCaptureKit for fully local recording. Capture system audio and mic simultaneously, with countdown, disk protection, and crash recovery. Trim head & tail and export — no third-party editor needed.",
        "区域 / 窗口 / 显示器三种录屏模式": "Region / window / display, three modes",
        "系统声音与麦克风同时录制，单一音轨": "System audio + mic, single mixed track",
        "倒计时与状态指示，录屏不打断": "Countdown & live status, no interruption",
        "异常退出后 Recovery 保留录制": "Crash recovery preserves the last clip",
        "头尾裁剪导出为新 MP4": "Trim head & tail, export a new MP4",
        "录屏与 GIF 录制需解锁 <strong>SnipX Pro</strong>（一次性买断，价格以 App Store 为准）。截屏、标注、长截图永久免费。":
            "Recording & GIF capture unlock with <strong>SnipX Pro</strong> (one-time purchase, price set in the App Store). Capture, annotation, and scrolling capture stay free, forever.",
        "零数据外传": "Zero data leaving your Mac",
        "完全离线运行": "Fully offline",
        "截图、录屏与 OCR 在本机处理，不自动上传内容或遥测。购买与恢复通过 Apple 服务完成。":
            "Capture, recording, and OCR are processed locally. Nothing is uploaded, and there is no telemetry. Purchases and restore go through Apple.",
        "购买与恢复可能需要联网": "Purchases & restore may need internet",
        "无账号、无登录、无云同步": "No account, no sign-in, no cloud sync",
        "无第三方 SDK、无埋点": "No third-party SDK, no trackers",
        "开源友好的本地存储": "Local-first storage, friendly to open source",
        # install
        "从 Mac App Store 获取": "Get it on the Mac App Store",
        "在 App Store 一键安装，内购、更新与恢复购买由 Apple 处理。":
            "One-click install on the App Store. Purchases, updates, and restore are handled by Apple.",
        "前往 App Store": "Go to the App Store",
        "点击下方按钮，跳转 Mac App Store 的 SnipX 应用页。": "Tap the button below to jump to SnipX on the Mac App Store.",
        "安装并打开": "Install & open",
        "点按「获取」安装 SnipX，完成后从「应用程序」或菜单栏打开。":
            "Tap \"Get\" to install SnipX, then launch from Applications or the menu bar.",
        "授权系统权限": "Grant system permissions",
        "按所用功能授权：屏幕录制、系统声音、麦克风和摄像头。":
            "Authorize per feature: screen recording, system audio, microphone, and camera.",
        "前往 App Store 下载": "Get SnipX on the App Store",
        "App Store 应用页即将上线，链接待回填。": "The App Store listing is coming soon — link will be filled in.",
        "macOS 14+ · Universal 2（Apple Silicon + Intel）· 仅 3 MB":
            "macOS 14+ · Universal 2 (Apple Silicon + Intel) · only 3 MB",
        "基础截屏永久免费 · 录屏与 GIF 录制需 <a href=\"./#about\">SnipX Pro</a>（一次性买断）":
            "Capture stays free forever · recording & GIF require <a href=\"./#about\">SnipX Pro</a> (one-time purchase)",
        # about
        "关于 SnipX": "About SnipX",
        "原生开发": "Built native",
        "Swift + AppKit + SwiftUI + ScreenCaptureKit + AVFoundation + Carbon 编写，无 WebView、无 Electron、无包装层。":
            "Written in Swift + AppKit + SwiftUI + ScreenCaptureKit + AVFoundation + Carbon. No WebView, no Electron, no wrapper layer.",
        "隐私优先": "Privacy first",
        "内容处理在本机，无需注册 SnipX 账号。购买由 Apple 处理；主动分享由你选择。详见":
            "All processing stays on your Mac — no SnipX account required. Purchases go through Apple; sharing is always your choice. Details in",
        "SnipX Pro": "SnipX Pro",
        "截屏、标注、长截图、置顶永久免费。一次性买断解锁 MP4 录屏与 GIF 录制，价格以 App Store 为准。":
            "Capture, annotation, scrolling capture, and pinning stay free forever. A one-time purchase unlocks MP4 recording and GIF capture. Price set in the App Store.",
        "持续维护": "Continuously maintained",
        "当前版本": "Current version",
        "每个版本均经过手测、单元测试、功能测试三道关。需要帮助？":
            "Every release goes through manual testing, unit tests, and functional tests. Need help?",
        "支持页": "support page",
        # footer
        "当前版本 1.0.0": "Current version 1.0.0",
        # images alt
        "SnipX 界面预览": "SnipX interface preview",
        "SnipX 菜单栏截屏入口": "SnipX menu bar capture entry",
        "SnipX 全局快捷键设置": "SnipX global shortcut settings",
        "SnipX 区域 / 窗口 / 全屏 / 长截图": "SnipX region / window / full screen / scrolling capture",
        "SnipX 本地 OCR 识别截图文字": "SnipX on-device OCR recognizes capture text",
        "SnipX 标注工具": "SnipX annotation tools",
        "SnipX MP4 录屏": "SnipX MP4 recording",
        "SnipX 完全离线运行": "SnipX runs fully offline",
        # privacy
        "Privacy Policy": "Privacy Policy",
        "SnipX 隐私政策": "SnipX Privacy Policy",
        "最后更新：2026 年 9 月 6 日 · 适用于 SnipX macOS 应用与本站": "Last updated: September 6, 2026 · applies to the SnipX macOS app and this website",
        "内容在本机处理": "Content is processed on-device",
        "截图、录屏、声音、摄像头画面、OCR 识别结果和标注均在你的 Mac 上处理。SnipX 不会自动把这些内容或本地诊断日志上传给开发者，不集成广告、追踪或第三方分析 SDK。":
            "Screenshots, recordings, audio, camera frames, OCR results, and annotations are all processed on your Mac. SnipX does not upload your content or local diagnostic logs, and does not embed ads, trackers, or third-party analytics SDKs.",
        "当你主动使用系统分享、发送反馈或将文件保存到云盘同步目录时，内容会按你的操作交给相应服务，其处理方式适用该服务的隐私政策。":
            "When you actively use system share, send feedback, or save files into a cloud-synced folder, the content is handed to the corresponding service per your action, and that service's privacy policy applies.",
        "1. 系统权限": "1. System permissions",
        "屏幕录制：": "Screen recording:",
        "用于截屏、长截图与录屏。": "required for capture, scrolling capture, and recording.",
        "系统声音：": "System audio:",
        "在你启用电脑声音录制时写入本地视频。": "written into the local video when you enable computer-audio capture.",
        "麦克风：": "Microphone:",
        "在你开启麦克风录制时申请，用于录制声音。": "requested only when you enable mic capture, for recording audio.",
        "摄像头：": "Camera:",
        "在你开启摄像头画面时申请，用于画中画。": "requested only when you enable camera overlay, for picture-in-picture.",
        "你可以在 macOS「系统设置 → 隐私与安全性」中管理权限。拒绝或撤销权限会影响对应功能。全局快捷键不要求额外开启辅助功能；在 Finder 中显示文件不要求自动化权限。":
            "You can manage permissions in macOS System Settings → Privacy & Security. Declining or revoking a permission disables the related features. Global shortcuts don't require Accessibility; revealing files in Finder doesn't require Automation.",
        "2. 文件、设置与本地日志": "2. Files, settings, and local logs",
        "截图与录屏通过保存对话框导出到你选择的位置。录屏过程文件保存在应用支持目录的 SnipX/Recovery 中；本地诊断日志保存在 Library/Logs/SnipX/CrashLogs 中。沙盒版的这些应用目录位于 macOS 为 SnipX 分配的容器内，开发测试版也可能使用项目旁的 CrashLogs 目录。":
            "Captures and recordings are exported via a save dialog to a location you choose. In-progress recordings live in the app's support directory under SnipX/Recovery; local diagnostic logs go to Library/Logs/SnipX/CrashLogs. In the sandbox build these directories live inside the macOS-assigned container for SnipX; the development build may also use a CrashLogs folder next to the project.",
        "应用在本机保存快捷键等偏好设置，并检查可用磁盘空间以保护录制文件。这些信息不会自动发送给开发者。OCR 使用 Apple Vision 框架在本机完成，不向服务器上传图片或识别结果。":
            "SnipX stores preferences such as shortcuts locally and checks available disk space to protect recordings. This data is not automatically sent to the developer. OCR runs on-device through the Apple Vision framework — images and recognition results never reach a server.",
        "删除应用本身不保证删除已导出文件、恢复文件和日志。请先保存需要保留的内容，再自行清理不需要的文件；不要在录制过程中删除恢复文件。":
            "Uninstalling SnipX does not guarantee deletion of exported files, recovery files, or logs. Save anything you want to keep first, then clean up files you no longer need. Don't delete recovery files while a recording is in progress.",
        "3. 购买与恢复购买": "3. Purchases & restore",
        "SnipX Pro 为一次性买断的非消耗型内购，价格以 App 内和 Apple 购买确认界面为准。商品加载、购买、恢复及交易状态同步通过 Apple StoreKit 服务完成，可能需要联网。":
            "SnipX Pro is a one-time-purchase non-consumable in-app purchase. The price is shown in the app and in Apple's purchase confirmation. Product loading, purchase, restore, and transaction-state sync go through Apple's StoreKit service and may require internet.",
        "Apple 处理付款。SnipX 在本机验证 Apple 提供的交易及权益信息，以决定是否解锁录屏和 GIF。开发者不通过应用收集你的银行卡或支付账户信息。Apple 对其处理的信息适用":
            "Apple handles payments. SnipX verifies the transaction and entitlement data Apple provides locally to decide whether to unlock recording and GIF. The developer does not collect your card or payment-account info through the app. For information Apple handles,",
        "Apple 隐私政策": "Apple's Privacy Policy applies",
        "4. 主动联系支持与访问官网": "4. Contacting support & visiting the site",
        "你主动发送邮件时，我们会收到你提供的邮箱、问题描述及附件，仅用于回复和排查问题。请勿发送无关的个人信息、密码或敏感截图；可以联系下方邮箱请求删除你提供的反馈材料。":
            "When you email us, we receive the email address, problem description, and any attachments you provide — used only to reply and debug. Please don't send unrelated personal info, passwords, or sensitive screenshots. You can email the address below to request deletion of your feedback materials.",
        "本站没有加入广告或分析 SDK。网站托管服务可能处理提供页面和保障服务所需的 IP 地址、浏览器请求及访问日志；这与应用在本机处理截图的行为不同。":
            "This site includes no ads or analytics SDKs. The hosting provider may process IP addresses, browser requests, and access logs needed to serve the site and keep it secure — that's separate from how the app processes captures locally.",
        "5. 政策变更与联系方式": "5. Changes & contact",
        "隐私处理方式变化时，我们会更新本页面及更新日期。隐私问题或删除反馈材料的请求请联系":
            "If our privacy practices change, we'll update this page and its date. For privacy questions or to request deletion of feedback materials, email",
        "使用说明见": "See usage notes at",
        "支持与帮助": "Support",
        # support
        "Support": "Support",
        "SnipX 支持与帮助": "SnipX Support",
        "FAQ、权限引导、反馈渠道 · 适用于 SnipX 1.0.0 及以上版本":
            "FAQ, permission guide, feedback channels · for SnipX 1.0.0 and later",
        "系统要求": "System requirements",
        "macOS 14.0 Sonoma 或更高版本": "macOS 14.0 Sonoma or later",
        "支持 Apple Silicon（M1 / M2 / M3 / M4）与 Intel Mac": "Apple Silicon (M1/M2/M3/M4) and Intel Macs",
        "通用构建（Universal 2）同时包含": "The Universal 2 build includes both",
        "截图、录屏与 OCR 在本机处理；商品加载、购买与恢复可能需要联网。":
            "Capture, recording, and OCR are processed on-device; product loading, purchase, and restore may require internet.",
        "首次启动：权限引导": "First launch: permission guide",
        "SnipX 只会在你实际使用对应功能时申请系统权限，遵循 macOS 默认流程，不会启动即弹窗。":
            "SnipX only asks for system permissions when you actually use the corresponding feature, following macOS defaults — no prompts at launch.",
        "首次截屏或录屏时系统会弹窗。授权后到「系统设置 → 隐私与安全性 → 屏幕录制」可看到 SnipX。":
            "macOS prompts on your first capture or recording. After you grant it, you'll see SnipX under System Settings → Privacy & Security → Screen Recording.",
        "仅在你开启「录制麦克风」开关时申请。": "Requested only when you enable mic capture.",
        "仅在你开启「录制摄像头」开关时申请。": "Requested only when you enable camera capture.",
        "录制电脑声音时，按 macOS 的屏幕与系统音频录制权限提示操作。":
            "When capturing computer audio, follow macOS's screen & system-audio capture prompt.",
        "如果误点了「拒绝」，可以到「系统设置 → 隐私与安全性」手动开启；SnipX 内置的「权限」面板也会引导你跳转到对应位置。":
            "If you tapped \"Don't Allow\" by mistake, you can enable it manually in System Settings → Privacy & Security. SnipX's built-in Permissions pane helps you jump to the right place.",
        "Q1：SnipX 联网吗？会上传我的截图吗？": "Q1: Does SnipX connect to the internet? Does it upload my captures?",
        "截图、录屏、OCR 与标注在本机处理，不会自动上传给开发者。购买与恢复通过 Apple 服务完成，可能需要联网；主动分享或发邮件时，内容按你的操作交给相应服务。":
            "Capture, recording, OCR, and annotation are processed on-device and never uploaded to the developer. Purchases and restore go through Apple and may need internet. If you actively share or email, the content is handed to the corresponding service per your action.",
        "Q2：SnipX Pro 是什么？哪些功能需要付费？": "Q2: What's SnipX Pro? What needs a purchase?",
        "截屏、标注、长截图、置顶、复制、保存、分享等基础功能永久免费。": "Capture, annotation, scrolling capture, pinning, copy, save, share, etc. stay free forever. ",
        "（一次性买断，价格以 Apple 购买界面为准）": "(one-time purchase, price set by Apple)",
        "解锁：": "unlocks:",
        "MP4 录屏（选定区域 / 显示器）": "MP4 recording (selected region / display)",
        "GIF 录制": "GIF capture",
        "系统声音 + 麦克风同时录制": "System audio + mic, simultaneously",
        "摄像头画中画": "Camera picture-in-picture",
        "倒计时与异常自动恢复": "Countdown & crash recovery",
        "头尾裁剪导出": "Trim head & tail, export",
        "Q3：如何恢复购买？": "Q3: How do I restore a purchase?",
        "打开 SnipX → 菜单栏 → 设置 → 录屏 → 付费墙卡底部「恢复购买」按钮。App 会通过 StoreKit 2 重新校验你的购买状态。":
            "Open SnipX → menu bar → Settings → Recording → tap \"Restore Purchase\" at the bottom of the paywall card. The app re-checks your purchase state via StoreKit 2.",
        "Q4：可以更换已授权的功能吗？": "Q4: Can I change a feature that's already authorized?",
        "截屏、标注、长截图的快捷键都可以在「设置 → 快捷键」中自定义，冲突时会自动提示。":
            "Shortcuts for capture, annotation, and scrolling capture are all customizable in Settings → Shortcuts, with conflict warnings.",
        "Q5：为什么我截不到 SnipX 自己的窗口？": "Q5: Why can't I capture SnipX's own window?",
        "SnipX 在录屏与截屏时会自动排除自身的菜单栏蒙层、操作浮层与录屏浮动条，避免污染画面。其他 SnipX 窗口（如设置、编辑录屏）默认会被正常捕获。":
            "During capture or recording, SnipX automatically excludes its own menu-bar overlays, action popovers, and the floating recording bar to keep the output clean. Other SnipX windows (like Settings or the recording editor) are captured normally.",
        "Q6：OCR 支持哪些语言？": "Q6: Which languages does OCR support?",
        "1.0.0 起，OCR 支持中文（简/繁）、英文及中英混合文本，由 Apple Vision 框架在本地完成识别，无网络依赖。":
            "From 1.0.0, OCR supports Simplified & Traditional Chinese, English, and mixed Chinese/English text, all recognized on-device through the Apple Vision framework — no network needed.",
        "Q7：录屏文件保存在哪里？": "Q7: Where do my recordings go?",
        "通过保存对话框导出到你选择的位置。录制过程文件保存在应用支持目录的 SnipX/Recovery 中，沙盒版位于 SnipX 的 macOS 容器内。应用会保留可恢复文件；退出前请先保存需要的内容。":
            "Exported via a save dialog to a location you choose. In-progress recordings live in SnipX/Recovery under the app's support directory (inside the sandbox container for the sandbox build). SnipX keeps recoverable files — save anything you want before quitting.",
        "反馈与问题上报": "Feedback & bug reports",
        "如果你遇到 bug、有功能建议或希望贡献想法：": "Found a bug, have a feature idea, or want to contribute?",
        "邮箱：": "Email:",
        "请附上：macOS 版本、SnipX 版本、复现步骤、必要时附截图或录屏":
            "Please include: macOS version, SnipX version, reproduction steps, and a screenshot or recording if possible",
        "SnipX 在异常退出时会保留崩溃日志到": "SnipX preserves crash logs at",
        "提交问题时一并附上可大幅加快定位": "include them in your report for much faster triage",
        "版本与更新": "Versions & updates",
        "当前最新版本：": "Current release:",
        "完整版本变更说明见": "Full release notes:",
        "相关链接": "Related links",
        "产品主页": "Product home",
    },
"ja": {
    # common
    "下载 SnipX": "SnipX をダウンロード",
    "主题：跟随系统": "テーマ：システムに合わせる",
    "主题：浅色": "テーマ：ライト",
    "主题：深色": "テーマ：ダーク",
    "特性": "機能",
    "下载": "ダウンロード",
    "关于": "概要",
    "查看功能": "機能を見る",
    "主页": "ホーム",
    "支持": "サポート",
    "隐私政策": "プライバシーポリシー",
    "© 2026 SnipX. All rights reserved.": "© 2026 SnipX. All rights reserved.",
    # hero
    "macOS 14+ · 原生应用": "macOS 14+ · ネイティブアプリ",
    "Mac 截屏与录屏，一触即达。": "Mac のスクリーンショットと録画を、ワンタップで。",
    "原生 AppKit + Swift + ScreenCaptureKit。物理像素输出、本地 OCR、可编辑快捷键、长截图拼接、本地 MP4 录制。内容在本机处理，无需注册 SnipX 账号。":
        "ネイティブ AppKit + Swift + ScreenCaptureKit。物理ピクセル出力、デバイス内 OCR、編集可能なショートカット、スクロールキャプチャ、デバイス内 MP4 録画。すべての処理は Mac 上で完結し、SnipX アカウントの登録は不要です。",
    "macOS 14+": "macOS 14+",
    "Universal 2 · Apple Silicon + Intel": "Universal 2 · Apple Silicon + Intel",
    "本地 OCR": "デバイス内 OCR",
    "SnipX Pro 录屏/GIF": "SnipX Pro 録画/GIF",
    "下载 SnipX": "SnipX をダウンロード",
    # features
    "菜单栏常驻，所见即可截": "メニューバーに常駐、見てすぐキャプチャ",
    "截屏、标注、录屏、长截图，全部在菜单栏一触即达。": "キャプチャ、注釈、録画、スクロールキャプチャを、メニューバーからワンタップで。",
    "常驻菜单栏": "メニューバーに常駐",
    "点击即开，不打扰": "クリックで開く、邪魔しない",
    "SnipX 始终浮于屏幕角落的菜单栏。无需打开主窗口，点击即弹出截屏 / 录屏入口。":
        "SnipX は画面端のメニューバーに静かに常駐します。メインウィンドウを開かなくても、ワンクリックでキャプチャ / 録画の入口が現れます。",
    "截屏、录屏、标注、设置 全部直达": "キャプチャ、録画、注釈、設定にワンタップでアクセス",
    "不抢焦点、不打扰当前工作": "フォーカスを奪わず、作業の邪魔をしない",
    "原生菜单栏图标，遵循 macOS 设计语言": "macOS のデザイン言語に準拠したネイティブのアイコン",
    "可编辑快捷键": "編集可能なショートカット",
    "全局快捷键，自由绑定": "グローバルショートカットを自由に割り当て",
    "截屏、录屏、标注、长截图 — 每个动作都可绑定独立快捷键，避免与其他应用冲突。":
        "キャプチャ、録画、注釈、スクロールキャプチャ — すべてのアクションに独立したショートカットを割り当てられ、競合があれば事前に警告します。",
    "支持单键 / 组合键 / 修饰键": "単一キー / 組み合わせ / 修飾キーに対応",
    "冲突检测，一键恢复默认": "競合検出とワンクリックでデフォルト復元",
    "录屏、截屏独立绑定，标注即时唤起": "録画とキャプチャは独立バインド、注釈は即時呼び出し",
    "四类截屏": "4 つのキャプチャモード",
    "区域 / 窗口 / 全屏 / 长截图": "範囲 / ウィンドウ / フルスクリーン / スクロール",
    "物理像素输出，自动按显示器倍率渲染。窗口截屏自动识别应用窗口边缘，长截图无缝拼接。":
        "物理ピクセル出力で、ディスプレイ倍率に合わせて自動レンダリング。ウィンドウキャプチャはアプリウィンドウの端を自動認識し、スクロールキャプチャは継ぎ目なく拼接します。",
    "区域截屏：拖拽选区，物理像素精度": "範囲キャプチャ：ドラッグで選択、物理ピクセル精度",
    "窗口截屏：自动选窗，背景透明": "ウィンドウキャプチャ：自動選択、背景透明",
    "全屏截屏：多显示器同时输出": "フルスクリーンキャプチャ：複数ディスプレイを同時に",
    "长截图：滚动拼接，自动对齐": "スクロールキャプチャ：自動拼接、ズレなし",
    "本地 OCR（1.0.0 新增）": "デバイス内 OCR（1.0.0 新機能）",
    "截图里的文字，一键识别": "キャプチャ内の文字をワンタップで認識",
    "基于 Apple Vision 框架，在你的 Mac 上直接识别截图中的中文、英文与中英混合文本。识别结果可编辑、可复制，不上传任何内容。":
        "Apple Vision フレームワークにより、Mac 上で直接キャプチャ内の中国語・英語・中英混在テキストを認識します。結果は編集・コピー可能で、何もアップロードしません。",
    "中文（简/繁）、英文与中英混排": "簡体字・繁体字・英語および中英混在",
    "完全本地识别，截图与文字不出本机": "完全ローカル認識、画像とテキストは Mac 内",
    "识别后可编辑、复制或取消": "認識後に編集、コピー、キャンセルが可能",
    "适用于截屏后的二次编辑与提取": "キャプチャ後の編集やテキスト抽出に最適",
    "标注工具": "注釈ツール",
    "矩形 / 箭头 / 文字 / 马赛克": "四角形 / 矢印 / テキスト / モザイク",
    "截屏后即时标注，所有元素可移动、可删除、可撤销重做。裁剪、马赛克、颜色选择器一应俱全。":
        "キャプチャ直後にすぐに注釈を追加でき、すべての要素は移動・削除・Undo / Redo が可能。クロップ、モザイク、カラーピッカーも標準搭載。",
    "矩形、椭圆、箭头、画笔、文字": "四角形、楕円、矢印、ペン、テキスト",
    "马赛克模糊敏感信息": "モザイクで機密情報をぼかす",
    "撤销 / 重做 / 裁剪 / 颜色选择器": "元に戻す / やり直し / クロップ / カラーピッカー",
    "本地 MP4 录屏 · SnipX Pro": "デバイス内 MP4 録画 · SnipX Pro",
    "倒计时 · 系统声 + 麦克风 · 自动恢复": "カウントダウン · システム音声 + マイク · 自動復元",
    "基于 ScreenCaptureKit 本地录制，支持同时录制系统声音与麦克风，倒计时、磁盘保护、异常恢复一应俱全。头尾裁剪导出，无需第三方编辑器。":
        "ScreenCaptureKit ベースのローカル録画で、システム音声とマイクの同時録音に対応。カウントダウン、ディスク保護、異常復元も万全。先頭と末尾をトリムして書き出せるので、サードパーティ製エディタは不要です。",
    "区域 / 窗口 / 显示器三种录屏模式": "範囲 / ウィンドウ / ディスプレイの 3 つの録画モード",
    "系统声音与麦克风同时录制，单一音轨": "システム音声とマイクを 1 つのトラックに同時録音",
    "倒计时与状态指示，录屏不打断": "カウントダウンと状態表示で録画を止めない",
    "异常退出后 Recovery 保留录制": "異常終了時は Recovery が録画を保護",
    "头尾裁剪导出为新 MP4": "先頭と末尾をトリムして新しい MP4 に書き出し",
    "录屏与 GIF 录制需解锁 <strong>SnipX Pro</strong>（一次性买断，价格以 App Store 为准）。截屏、标注、长截图永久免费。":
        "録画と GIF 録画は <strong>SnipX Pro</strong>（買い切り、価格は App Store 準拠）のロック解除が必要です。キャプチャ、注釈、スクロールキャプチャは永久無料です。",
    "零数据外传": "データは一切外部送信されません",
    "完全离线运行": "完全オフラインで動作",
    "截图、录屏与 OCR 在本机处理，不自动上传内容或遥测。购买与恢复通过 Apple 服务完成。":
        "キャプチャ、録画、OCR は Mac 上で処理され、コンテンツやテレメトリの自動アップロードは行いません。購入と復元は Apple のサービスを経由します。",
    "购买与恢复可能需要联网": "購入と復元にはネット接続が必要な場合があります",
    "无账号、无登录、无云同步": "アカウント・ログイン・クラウド同期なし",
    "无第三方 SDK、无埋点": "サードパーティ SDK・トラッカーなし",
    "开源友好的本地存储": "オープンソースに配慮したローカルストレージ",
    # install
    "从 Mac App Store 获取": "Mac App Store で入手",
    "在 App Store 一键安装，内购、更新与恢复购买由 Apple 处理。":
        "App Store でワンクリックインストール。アプリ内課金、アップデート、購入復元は Apple が処理します。",
    "前往 App Store": "App Store を開く",
    "点击下方按钮，跳转 Mac App Store 的 SnipX 应用页。": "下のボタンをクリックすると、Mac App Store の SnipX ページに移動します。",
    "安装并打开": "インストールして開く",
    "点按「获取」安装 SnipX，完成后从「应用程序」或菜单栏打开。":
        "「入手」をクリックして SnipX をインストールし、完了後は「アプリケーション」フォルダまたはメニューバーから起動してください。",
    "授权系统权限": "システム権限を許可",
    "按所用功能授权：屏幕录制、系统声音、麦克风和摄像头。":
        "使用する機能に応じて許可：画面収録、システム音声、マイク、カメラ。",
    "前往 App Store 下载": "App Store でダウンロード",
    "App Store 应用页即将上线，链接待回填。": "App Store ページは近日公開予定です。リンクは決まり次第反映します。",
    "macOS 14+ · Universal 2（Apple Silicon + Intel）· 仅 3 MB":
        "macOS 14+ · Universal 2（Apple Silicon + Intel）· わずか 3 MB",
    "基础截屏永久免费 · 录屏与 GIF 录制需 <a href=\"./#about\">SnipX Pro</a>（一次性买断）":
        "基本キャプチャは永久無料 · 録画と GIF 録画は <a href=\"./#about\">SnipX Pro</a>（買い切り）が必要",
    # about
    "关于 SnipX": "SnipX について",
    "原生开发": "ネイティブ開発",
    "Swift + AppKit + SwiftUI + ScreenCaptureKit + AVFoundation + Carbon 编写，无 WebView、无 Electron、无包装层。":
        "Swift + AppKit + SwiftUI + ScreenCaptureKit + AVFoundation + Carbon で記述。WebView も Electron もラッパー層もありません。",
    "隐私优先": "プライバシーを最優先",
    "内容处理在本机，无需注册 SnipX 账号。购买由 Apple 处理；主动分享由你选择。详见":
        "コンテンツ処理はすべて Mac 上で完結し、SnipX アカウントの登録は不要です。購入は Apple が処理し、能動的な共有はあなたの選択次第です。詳しくは",
    "SnipX Pro": "SnipX Pro",
    "截屏、标注、长截图、置顶永久免费。一次性买断解锁 MP4 录屏与 GIF 录制，价格以 App Store 为准。":
        "キャプチャ、注釈、スクロールキャプチャ、ピン留めは永久無料。MP4 録画と GIF 録画は買い切りでロック解除、価格は App Store 準拠です。",
    "持续维护": "継続的にメンテナンス",
    "当前版本": "現在のバージョン",
    "每个版本均经过手测、单元测试、功能测试三道关。需要帮助？":
        "すべてのバージョンは手動テスト、ユニットテスト、機能テストの三段階をクリアしています。ヘルプが必要ですか？",
    "支持页": "サポートページ",
    # footer
    "当前版本 1.0.0": "現在のバージョン 1.0.0",
    # images alt
    "SnipX 界面预览": "SnipX インターフェースのプレビュー",
    "SnipX 菜单栏截屏入口": "SnipX メニューバーのキャプチャ入口",
    "SnipX 全局快捷键设置": "SnipX グローバルショートカット設定",
    "SnipX 区域 / 窗口 / 全屏 / 长截图": "SnipX 範囲 / ウィンドウ / フルスクリーン / スクロールキャプチャ",
    "SnipX 本地 OCR 识别截图文字": "SnipX デバイス内 OCR でキャプチャ内テキストを認識",
    "SnipX 标注工具": "SnipX 注釈ツール",
    "SnipX MP4 录屏": "SnipX MP4 録画",
    "SnipX 完全离线运行": "SnipX は完全オフラインで動作",
    # privacy
    "Privacy Policy": "Privacy Policy",
    "SnipX 隐私政策": "SnipX プライバシーポリシー",
    "最后更新：2026 年 9 月 6 日 · 适用于 SnipX macOS 应用与本站": "最終更新日：2026 年 9 月 6 日 · SnipX macOS アプリおよび本サイトに適用",
    "内容在本机处理": "コンテンツは Mac 上で処理",
    "截图、录屏、声音、摄像头画面、OCR 识别结果和标注均在你的 Mac 上处理。SnipX 不会自动把这些内容或本地诊断日志上传给开发者，不集成广告、追踪或第三方分析 SDK。":
        "スクリーンショット、録画、音声、カメラ映像、OCR 認識結果、注釈はすべて Mac 上で処理されます。SnipX はコンテンツやローカル診断ログを開発者に自動アップロードせず、広告、トラッカー、サードパーティ分析 SDK も組み込みません。",
    "当你主动使用系统分享、发送反馈或将文件保存到云盘同步目录时，内容会按你的操作交给相应服务，其处理方式适用该服务的隐私政策。":
        "能動的にシステム共有を使用したり、フィードバックを送信したり、ファイルをクラウド同期フォルダに保存した場合、コンテンツはあなたの操作に応じて対応するサービスに引き渡され、そのサービスのプライバシーポリシーが適用されます。",
    "1. 系统权限": "1. システム権限",
    "屏幕录制：": "画面収録：",
    "用于截屏、长截图与录屏。": "キャプチャ、スクロールキャプチャ、録画に使用されます。",
    "系统声音：": "システム音声：",
    "在你启用电脑声音录制时写入本地视频。": "パソコン音声の録音有効時にローカル動画に書き込まれます。",
    "麦克风：": "マイク：",
    "在你开启麦克风录制时申请，用于录制声音。": "マイク録音を有効にした場合にのみ要求され、音声録音に使用されます。",
    "摄像头：": "カメラ：",
    "在你开启摄像头画面时申请，用于画中画。": "カメラオーバーレイを有効にした場合にのみ要求され、PiP に使用されます。",
    "你可以在 macOS「系统设置 → 隐私与安全性」中管理权限。拒绝或撤销权限会影响对应功能。全局快捷键不要求额外开启辅助功能；在 Finder 中显示文件不要求自动化权限。":
        "macOS の「システム設定 → プライバシーとセキュリティ」で権限を管理できます。権限を拒否または取り消すと対応する機能は無効になります。グローバルショートカットはアクセシビリティを要求せず、Finder でのファイル表示もオートメーション権限を要求しません。",
    "2. 文件、设置与本地日志": "2. ファイル、設定、ローカルログ",
    "截图与录屏通过保存对话框导出到你选择的位置。录屏过程文件保存在应用支持目录的 SnipX/Recovery 中；本地诊断日志保存在 Library/Logs/SnipX/CrashLogs 中。沙盒版的这些应用目录位于 macOS 为 SnipX 分配的容器内，开发测试版也可能使用项目旁的 CrashLogs 目录。":
        "キャプチャと録画は保存ダイアログで選択した場所に書き出されます。録画中ファイルはアプリサポートディレクトリの SnipX/Recovery に保存され、ローカル診断ログは Library/Logs/SnipX/CrashLogs に保存されます。サンドボックス版のこれらのディレクトリは、macOS が SnipX に割り当てたコンテナ内にあります。開発ビルドではプロジェクト隣の CrashLogs ディレクトリも使用される場合があります。",
    "应用在本机保存快捷键等偏好设置，并检查可用磁盘空间以保护录制文件。这些信息不会自动发送给开发者。OCR 使用 Apple Vision 框架在本机完成，不向服务器上传图片或识别结果。":
        "アプリはショートカットなどの設定をローカルに保存し、録画ファイルを保護するために利用可能なディスク容量を確認します。これらの情報は自動で開発者に送信されません。OCR は Apple Vision フレームワークでローカル実行され、画像や認識結果がサーバーに送信されることはありません。",
    "删除应用本身不保证删除已导出文件、恢复文件和日志。请先保存需要保留的内容，再自行清理不需要的文件；不要在录制过程中删除恢复文件。":
        "アプリをアンインストールしても、書き出し済みファイル、復元ファイル、ログは自動削除されません。残したい内容は先に保存し、不要なファイルは各自で削除してください。録画進行中に復元ファイルを削除しないでください。",
    "3. 购买与恢复购买": "3. 購入と購入復元",
    "SnipX Pro 为一次性买断的非消耗型内购，价格以 App 内和 Apple 购买确认界面为准。商品加载、购买、恢复及交易状态同步通过 Apple StoreKit 服务完成，可能需要联网。":
        "SnipX Pro は買い切りの非消耗型アプリ内課金で、価格はアプリ内および Apple の購入確認画面に従います。商品ロード、購入、復元、取引状態の同期は Apple の StoreKit サービス経由で行われ、ネット接続が必要な場合があります。",
    "Apple 处理付款。SnipX 在本机验证 Apple 提供的交易及权益信息，以决定是否解锁录屏和 GIF。开发者不通过应用收集你的银行卡或支付账户信息。Apple 对其处理的信息适用":
        "決済は Apple が処理します。SnipX は Apple から提供された取引およびエンタイトルメント情報をローカルで検証し、録画と GIF のロック解除を判定します。デベロッパはアプリを通じてあなたのカードや支払いアカウント情報を収集しません。Apple が取り扱う情報には",
    "Apple 隐私政策": "Apple のプライバシーポリシーが適用されます",
    "4. 主动联系支持与访问官网": "4. サポートへの能動的な連絡と公式サイト閲覧",
    "你主动发送邮件时，我们会收到你提供的邮箱、问题描述及附件，仅用于回复和排查问题。请勿发送无关的个人信息、密码或敏感截图；可以联系下方邮箱请求删除你提供的反馈材料。":
        "あなたが能動的にメールを送った場合、記載されたメールアドレス、問題の説明、添付ファイルを受信し、返信と問題の調査にのみ使用します。無関係な個人情報、パスワード、機密性の高いスクリーンショットは送らないでください。提供したフィードバック資料の削除依頼は下記のメールアドレスまでご連絡ください。",
    "本站没有加入广告或分析 SDK。网站托管服务可能处理提供页面和保障服务所需的 IP 地址、浏览器请求及访问日志；这与应用在本机处理截图的行为不同。":
        "本サイトは広告や分析 SDK を一切組み込んでいません。ホスティングサービスはページの提供とサービス維持に必要な IP アドレス、ブラウザリクエスト、アクセスログを処理する場合がありますが、これはアプリがローカルでキャプチャを処理する仕組みとは異なります。",
    "5. 政策变更与联系方式": "5. ポリシーの変更と連絡先",
    "隐私处理方式变化时，我们会更新本页面及更新日期。隐私问题或删除反馈材料的请求请联系":
        "プライバシー取り扱いを変更する際は、本ページと更新日を更新します。プライバシーに関するご質問やフィードバック資料の削除依頼は下記までご連絡ください",
    "使用说明见": "使い方は",
    "支持与帮助": "サポート",
    # support
    "Support": "Support",
    "SnipX 支持与帮助": "SnipX サポート",
    "FAQ、权限引导、反馈渠道 · 适用于 SnipX 1.0.0 及以上版本":
        "FAQ、権限ガイド、フィードバック窓口 · SnipX 1.0.0 以降に対応",
    "系统要求": "システム要件",
    "macOS 14.0 Sonoma 或更高版本": "macOS 14.0 Sonoma 以降",
    "支持 Apple Silicon（M1 / M2 / M3 / M4）与 Intel Mac": "Apple Silicon（M1 / M2 / M3 / M4）と Intel Mac に対応",
    "通用构建（Universal 2）同时包含": "Universal 2 ビルドには次の両方が含まれます",
    "截图、录屏与 OCR 在本机处理；商品加载、购买与恢复可能需要联网。":
        "キャプチャ、録画、OCR は Mac 上で処理されます。商品ロード、購入、復元にはネット接続が必要な場合があります。",
    "首次启动：权限引导": "初回起動：権限ガイド",
    "SnipX 只会在你实际使用对应功能时申请系统权限，遵循 macOS 默认流程，不会启动即弹窗。":
        "SnipX は対応する機能を実際に使ったときのみシステム権限を要求します。macOS のデフォルトフローに従い、起動直後にダイアログは表示しません。",
    "首次截屏或录屏时系统会弹窗。授权后到「系统设置 → 隐私与安全性 → 屏幕录制」可看到 SnipX。":
        "初回キャプチャまたは録画時に macOS がダイアログを表示します。許可すると「システム設定 → プライバシーとセキュリティ → 画面収録」に SnipX が表示されます。",
    "仅在你开启「录制麦克风」开关时申请。": "マイク録音を有効にした場合にのみ要求されます。",
    "仅在你开启「录制摄像头」开关时申请。": "カメラキャプチャを有効にした場合にのみ要求されます。",
    "录制电脑声音时，按 macOS 的屏幕与系统音频录制权限提示操作。":
        "パソコン音声を録音する際は、macOS の画面とシステム音声の録音プロンプトに従ってください。",
    "如果误点了「拒绝」，可以到「系统设置 → 隐私与安全性」手动开启；SnipX 内置的「权限」面板也会引导你跳转到对应位置。":
        "誤って「許可しない」をタップした場合は、「システム設定 → プライバシーとセキュリティ」で手動で有効化できます。SnipX 内蔵の「権限」パネルからも該当箇所へ誘導されます。",
    "Q1：SnipX 联网吗？会上传我的截图吗？": "Q1：SnipX はネット接続しますか？キャプチャをアップロードしますか？",
    "截图、录屏、OCR 与标注在本机处理，不会自动上传给开发者。购买与恢复通过 Apple 服务完成，可能需要联网；主动分享或发邮件时，内容按你的操作交给相应服务。":
        "キャプチャ、録画、OCR、注釈はローカル処理され、開発者に自動アップロードされることはありません。購入と復元は Apple 経由で行われ、ネット接続が必要な場合があります。能動的に共有やメール送信を行った場合、コンテンツはあなたの操作に応じて対応サービスに引き渡されます。",
    "Q2：SnipX Pro 是什么？哪些功能需要付费？": "Q2：SnipX Pro とは？どの機能が有料ですか？",
    "截屏、标注、长截图、置顶、复制、保存、分享等基础功能永久免费。": "キャプチャ、注釈、スクロールキャプチャ、ピン留め、コピー、保存、共有などの基本機能は永久無料です。",
    "（一次性买断，价格以 Apple 购买界面为准）": "（買い切り、価格は Apple の購入画面に準拠）",
    "解锁：": "ロック解除で解放：",
    "MP4 录屏（选定区域 / 显示器）": "MP4 録画（選択範囲 / ディスプレイ）",
    "GIF 录制": "GIF 録画",
    "系统声音 + 麦克风同时录制": "システム音声 + マイク同時録音",
    "摄像头画中画": "カメラ PiP",
    "倒计时与异常自动恢复": "カウントダウンと異常時の自動復元",
    "头尾裁剪导出": "先頭・末尾をトリムして書き出し",
    "Q3：如何恢复购买？": "Q3：購入を復元するには？",
    "打开 SnipX → 菜单栏 → 设置 → 录屏 → 付费墙卡底部「恢复购买」按钮。App 会通过 StoreKit 2 重新校验你的购买状态。":
        "SnipX を開く → メニューバー → 設定 → 録画 → ペイウォールカード下部の「購入を復元」ボタンをタップ。アプリが StoreKit 2 で購入状態を再検証します。",
    "Q4：可以更换已授权的功能吗？": "Q4：既に有効化された機能を変更できますか？",
    "截屏、标注、长截图的快捷键都可以在「设置 → 快捷键」中自定义，冲突时会自动提示。":
        "キャプチャ、注釈、スクロールキャプチャのショートカットは「設定 → ショートカット」でカスタマイズでき、競合時は自動で警告されます。",
    "Q5：为什么我截不到 SnipX 自己的窗口？": "Q5：なぜ SnipX 自身のウィンドウをキャプチャできないのですか？",
    "SnipX 在录屏与截屏时会自动排除自身的菜单栏蒙层、操作浮层与录屏浮动条，避免污染画面。其他 SnipX 窗口（如设置、编辑录屏）默认会被正常捕获。":
        "SnipX は録画とキャプチャ時に自身のメニューバーオーバーレイ、操作ポップオーバー、録画フローティングバーを自動的に除外し、出力をクリーンに保ちます。その他の SnipX ウィンドウ（設定や録画エディタなど）は通常通りキャプチャされます。",
    "Q6：OCR 支持哪些语言？": "Q6：OCR はどの言語に対応していますか？",
    "1.0.0 起，OCR 支持中文（简/繁）、英文及中英混合文本，由 Apple Vision 框架在本地完成识别，无网络依赖。":
        "1.0.0 より、OCR は簡体字・繁体字・英語および中英混在テキストに対応し、Apple Vision フレームワークによりローカルで認識されるためネットワークに依存しません。",
    "Q7：录屏文件保存在哪里？": "Q7：録画ファイルはどこに保存されますか？",
    "通过保存对话框导出到你选择的位置。录制过程文件保存在应用支持目录的 SnipX/Recovery 中，沙盒版位于 SnipX 的 macOS 容器内。应用会保留可恢复文件；退出前请先保存需要的内容。":
        "保存ダイアログで選択した場所に書き出されます。録画中ファイルはアプリサポートディレクトリの SnipX/Recovery に保存され、サンドボックス版では SnipX の macOS コンテナ内にあります。アプリは復元可能なファイルを保持するため、終了前に必要な内容を保存してください。",
    "反馈与问题上报": "フィードバックとバグ報告",
    "如果你遇到 bug、有功能建议或希望贡献想法：": "バグを見つけた場合、機能提案がある場合、アイデアを共有したい場合：",
    "邮箱：": "メール：",
    "请附上：macOS 版本、SnipX 版本、复现步骤、必要时附截图或录屏":
        "次の情報を添付してください：macOS バージョン、SnipX バージョン、再現手順、必要に応じてスクリーンショットまたは録画",
    "SnipX 在异常退出时会保留崩溃日志到": "SnipX は異常終了時にクラッシュログを次に保存します：",
    "提交问题时一并附上可大幅加快定位": "報告に添付いただくと調査が大幅に早まります",
    "版本与更新": "バージョンとアップデート",
    "当前最新版本：": "最新バージョン：",
    "完整版本变更说明见": "完全な変更履歴は",
    "相关链接": "関連リンク",
    "产品主页": "製品ホーム",
},
"ko": {
    # common
    "下载 SnipX": "SnipX 다운로드",
    "主题：跟随系统": "테마: 시스템과 동기화",
    "主题：浅色": "테마: 라이트",
    "主题：深色": "테마: 다크",
    "特性": "기능",
    "下载": "다운로드",
    "关于": "정보",
    "查看功能": "기능 보기",
    "主页": "홈",
    "支持": "지원",
    "隐私政策": "개인정보 처리방침",
    "© 2026 SnipX. All rights reserved.": "© 2026 SnipX. All rights reserved.",
    # hero
    "macOS 14+ · 原生应用": "macOS 14+ · 네이티브 앱",
    "Mac 截屏与录屏，一触即达。": "Mac 스크린샷과 화면 녹화를 한 번의 탭으로.",
    "原生 AppKit + Swift + ScreenCaptureKit。物理像素输出、本地 OCR、可编辑快捷键、长截图拼接、本地 MP4 录制。内容在本机处理，无需注册 SnipX 账号。":
        "네이티브 AppKit + Swift + ScreenCaptureKit. 물리 픽셀 출력, 온디바이스 OCR, 편집 가능한 단축키, 스크롤 캡처, 로컬 MP4 녹화까지. 모든 처리는 Mac에서 이루어지며 SnipX 계정 가입은 필요 없습니다.",
    "macOS 14+": "macOS 14+",
    "Universal 2 · Apple Silicon + Intel": "Universal 2 · Apple Silicon + Intel",
    "本地 OCR": "온디바이스 OCR",
    "SnipX Pro 录屏/GIF": "SnipX Pro 녹화/GIF",
    "下载 SnipX": "SnipX 다운로드",
    # features
    "菜单栏常驻，所见即可截": "메뉴바에 상주, 보이는 대로 캡처",
    "截屏、标注、录屏、长截图，全部在菜单栏一触即达。": "캡처, 주석, 녹화, 스크롤 캡처까지 메뉴바에서 한 번의 탭으로.",
    "常驻菜单栏": "메뉴바 상주",
    "点击即开，不打扰": "탭하면 열리고, 방해하지 않음",
    "SnipX 始终浮于屏幕角落的菜单栏。无需打开主窗口，点击即弹出截屏 / 录屏入口。":
        "SnipX는 화면 구석 메뉴바에 조용히 상주합니다. 메인 창을 열 필요 없이 한 번의 탭으로 캡처 / 녹화 진입점이 나타납니다.",
    "截屏、录屏、标注、设置 全部直达": "캡처, 녹화, 주석, 설정 한 번에 접근",
    "不抢焦点、不打扰当前工作": "포커스를 빼앗지 않고 작업 흐름을 깨지 않음",
    "原生菜单栏图标，遵循 macOS 设计语言": "macOS 디자인 언어를 따르는 네이티브 메뉴바 아이콘",
    "可编辑快捷键": "편집 가능한 단축키",
    "全局快捷键，自由绑定": "전역 단축키를 자유롭게 지정",
    "截屏、录屏、标注、长截图 — 每个动作都可绑定独立快捷键，避免与其他应用冲突。":
        "캡처, 녹화, 주석, 스크롤 캡처 — 모든 동작에 독립적인 단축키를 지정할 수 있고, 충돌 시 미리 경고합니다.",
    "支持单键 / 组合键 / 修饰键": "단일 키 / 조합 키 / 보조 키 지원",
    "冲突检测，一键恢复默认": "충돌 감지 및 원 클릭 기본값 복원",
    "录屏、截屏独立绑定，标注即时唤起": "녹화와 캡처 독립 바인딩, 주석 즉시 호출",
    "四类截屏": "네 가지 캡처 모드",
    "区域 / 窗口 / 全屏 / 长截图": "영역 / 창 / 전체 화면 / 스크롤",
    "物理像素输出，自动按显示器倍率渲染。窗口截屏自动识别应用窗口边缘，长截图无缝拼接。":
        "물리 픽셀 출력으로 디스플레이 배율에 맞춰 자동 렌더링. 창 캡처는 앱 창 가장자리를 자동 인식하고, 스크롤 캡처는 매끄럽게 이어 붙입니다.",
    "区域截屏：拖拽选区，物理像素精度": "영역 캡처: 드래그 선택, 물리 픽셀 정밀도",
    "窗口截屏：自动选窗，背景透明": "창 캡처: 자동 선택, 배경 투명",
    "全屏截屏：多显示器同时输出": "전체 화면 캡처: 여러 디스플레이 동시 출력",
    "长截图：滚动拼接，自动对齐": "스크롤 캡처: 자동 이어 붙이기, 어긋남 없음",
    "本地 OCR（1.0.0 新增）": "온디바이스 OCR (1.0.0 신규)",
    "截图里的文字，一键识别": "캡처 안의 텍스트를 한 번의 탭으로 인식",
    "基于 Apple Vision 框架，在你的 Mac 上直接识别截图中的中文、英文与中英混合文本。识别结果可编辑、可复制，不上传任何内容。":
        "Apple Vision 프레임워크 기반으로 Mac에서 직접 중국어, 영어, 중영 혼합 텍스트를 인식합니다. 결과는 편집 및 복사 가능하며, 어떤 내용도 업로드하지 않습니다.",
    "中文（简/繁）、英文与中英混排": "간체 / 번체 중국어, 영어 및 중영 혼합",
    "完全本地识别，截图与文字不出本机": "완전 로컬 인식, 이미지와 텍스트는 Mac 밖으로 나가지 않음",
    "识别后可编辑、复制或取消": "인식 후 편집, 복사 또는 취소 가능",
    "适用于截屏后的二次编辑与提取": "캡처 후 추가 편집 및 텍스트 추출에 적합",
    "标注工具": "주석 도구",
    "矩形 / 箭头 / 文字 / 马赛克": "사각형 / 화살표 / 텍스트 / 모자이크",
    "截屏后即时标注，所有元素可移动、可删除、可撤销重做。裁剪、马赛克、颜色选择器一应俱全。":
        "캡처 직후 즉시 주석을 추가하고, 모든 요소를 이동, 삭제, 실행 취소 / 다시 실행할 수 있습니다. 자르기, 모자이크, 색상 선택기까지 모두 기본 제공.",
    "矩形、椭圆、箭头、画笔、文字": "사각형, 타원, 화살표, 펜, 텍스트",
    "马赛克模糊敏感信息": "모자이크로 민감 정보 흐림 처리",
    "撤销 / 重做 / 裁剪 / 颜色选择器": "실행 취소 / 다시 실행 / 자르기 / 색상 선택기",
    "本地 MP4 录屏 · SnipX Pro": "로컬 MP4 녹화 · SnipX Pro",
    "倒计时 · 系统声 + 麦克风 · 自动恢复": "카운트다운 · 시스템 음성 + 마이크 · 자동 복구",
    "基于 ScreenCaptureKit 本地录制，支持同时录制系统声音与麦克风，倒计时、磁盘保护、异常恢复一应俱全。头尾裁剪导出，无需第三方编辑器。":
        "ScreenCaptureKit 기반 로컬 녹화로 시스템 음성과 마이크 동시 녹음을 지원하며, 카운트다운, 디스크 보호, 비정상 종료 복구까지 갖췄습니다. 머리와 꼬리를 잘라 내보내면 타사 편집기가 필요 없습니다.",
    "区域 / 窗口 / 显示器三种录屏模式": "영역 / 창 / 디스플레이 세 가지 녹화 모드",
    "系统声音与麦克风同时录制，单一音轨": "시스템 음성과 마이크를 단일 트랙에 동시 녹음",
    "倒计时与状态指示，录屏不打断": "카운트다운과 상태 표시로 녹화를 방해하지 않음",
    "异常退出后 Recovery 保留录制": "비정상 종료 시 Recovery가 녹화를 보존",
    "头尾裁剪导出为新 MP4": "머리와 꼬리를 잘라 새 MP4로 내보내기",
    "录屏与 GIF 录制需解锁 <strong>SnipX Pro</strong>（一次性买断，价格以 App Store 为准）。截屏、标注、长截图永久免费。":
        "녹화와 GIF 녹화는 <strong>SnipX Pro</strong> (일회성 구매, 가격은 App Store 기준)의 잠금 해제가 필요합니다. 캡처, 주석, 스크롤 캡처는 영원히 무료입니다.",
    "零数据外传": "데이터 외부 전송 없음",
    "完全离线运行": "완전 오프라인 작동",
    "截图、录屏与 OCR 在本机处理，不自动上传内容或遥测。购买与恢复通过 Apple 服务完成。":
        "캡처, 녹화, OCR은 Mac에서 처리되며 콘텐츠나 텔레메트리 자동 업로드는 없습니다. 구매와 복원은 Apple 서비스를 통해 처리됩니다.",
    "购买与恢复可能需要联网": "구매와 복구에는 인터넷 연결이 필요할 수 있음",
    "无账号、无登录、无云同步": "계정, 로그인, 클라우드 동기화 없음",
    "无第三方 SDK、无埋点": "타사 SDK 및 트래커 없음",
    "开源友好的本地 저장": "오픈 소스에 친화적인 로컬 저장",
    # install
    "从 Mac App Store 获取": "Mac App Store에서 받기",
    "在 App Store 一键安装，内购、更新与恢复购买由 Apple 处理。":
        "App Store에서 한 번의 탭으로 설치. 인앱 구매, 업데이트, 구매 복구는 Apple이 처리합니다.",
    "前往 App Store": "App Store로 이동",
    "点击下方按钮，跳转 Mac App Store 的 SnipX 应用页。": "아래 버튼을 누르면 Mac App Store의 SnipX 앱 페이지로 이동합니다.",
    "安装并打开": "설치하고 열기",
    "点按「获取」安装 SnipX，完成后从「应用程序」或菜单栏打开。":
        "「받기」를 눌러 SnipX를 설치하고 완료되면 「응용 프로그램」 또는 메뉴바에서 실행하세요.",
    "授权系统权限": "시스템 권한 허용",
    "按所用功能授权：屏幕录制、系统声音、麦克风和摄像头。":
        "사용 기능별로 허용: 화면 녹화, 시스템 음성, 마이크, 카메라.",
    "前往 App Store 下载": "App Store에서 다운로드",
    "App Store 应用页即将上线，链接待回填。": "App Store 앱 페이지는 곧 공개됩니다. 링크는 확정 후 반영됩니다.",
    "macOS 14+ · Universal 2（Apple Silicon + Intel）· 仅 3 MB":
        "macOS 14+ · Universal 2 (Apple Silicon + Intel) · 단 3 MB",
    "基础截屏永久免费 · 录屏与 GIF 录制需 <a href=\"./#about\">SnipX Pro</a>（一次性买断）":
        "기본 캡처는 영구 무료 · 녹화와 GIF 녹화는 <a href=\"./#about\">SnipX Pro</a> (일회성 구매) 필요",
    # about
    "关于 SnipX": "SnipX 정보",
    "原生开发": "네이티브 개발",
    "Swift + AppKit + SwiftUI + ScreenCaptureKit + AVFoundation + Carbon 编写，无 WebView、无 Electron、无包装层。":
        "Swift + AppKit + SwiftUI + ScreenCaptureKit + AVFoundation + Carbon으로 작성. WebView, Electron, 래퍼 레이어 없음.",
    "隐私优先": "프라이버시 최우선",
    "内容处理在本机，无需注册 SnipX 账号。购买由 Apple 处理；主动分享由你选择。详见":
        "콘텐츠 처리는 Mac에서 이루어지며 SnipX 계정 가입이 필요 없습니다. 구매는 Apple이 처리하고 능동적 공유는 사용자가 선택합니다. 자세한 내용은",
    "SnipX Pro": "SnipX Pro",
    "截屏、标注、长截图、置顶永久免费。一次性买断解锁 MP4 录屏与 GIF 录制，价格以 App Store 为准。":
        "캡처, 주석, 스크롤 캡처, 고정하기는 영구 무료. MP4 녹화와 GIF 녹화는 일회성 구매로 잠금 해제되며 가격은 App Store 기준입니다.",
    "持续维护": "지속적인 유지보수",
    "当前版本": "현재 버전",
    "每个版本均经过手测、单元测试、功能测试三道关。需要帮助？":
        "모든 버전은 수동 테스트, 단위 테스트, 기능 테스트 세 단계를 거칩니다. 도움이 필요하신가요?",
    "支持页": "지원 페이지",
    # footer
    "当前版本 1.0.0": "현재 버전 1.0.0",
    # images alt
    "SnipX 界面预览": "SnipX 인터페이스 미리보기",
    "SnipX 菜单栏截屏入口": "SnipX 메뉴바 캡처 진입점",
    "SnipX 全局快捷键设置": "SnipX 전역 단축키 설정",
    "SnipX 区域 / 窗口 / 全屏 / 长截图": "SnipX 영역 / 창 / 전체 화면 / 스크롤 캡처",
    "SnipX 本地 OCR 识别截图文字": "SnipX 온디바이스 OCR로 캡처 텍스트 인식",
    "SnipX 标注工具": "SnipX 주석 도구",
    "SnipX MP4 录屏": "SnipX MP4 녹화",
    "SnipX 完全离线运行": "SnipX 완전 오프라인 작동",
    # privacy
    "Privacy Policy": "Privacy Policy",
    "SnipX 隐私政策": "SnipX 개인정보 처리방침",
    "最后更新：2026 年 9 月 6 日 · 适用于 SnipX macOS 应用与本站": "최종 업데이트: 2026년 9월 6일 · SnipX macOS 앱 및 본 사이트에 적용",
    "内容在本机处理": "콘텐츠는 Mac에서 처리됩니다",
    "截图、录屏、声音、摄像头画面、OCR 识别结果和标注均在你的 Mac 上处理。SnipX 不会自动把这些内容或本地诊断日志上传给开发者，不集成广告、追踪或第三方分析 SDK。":
        "스크린샷, 녹화, 음성, 카메라 영상, OCR 인식 결과 및 주석은 모두 Mac에서 처리됩니다. SnipX는 콘텐츠나 로컬 진단 로그를 개발자에게 자동으로 업로드하지 않으며, 광고, 트래커, 타사 분석 SDK를 포함하지 않습니다.",
    "当你主动使用系统分享、发送反馈或将文件保存到云盘同步目录时，内容会按你的操作交给相应服务，其处理方式适用该服务的隐私政策。":
        "사용자가 시스템 공유를 사용하거나, 피드백을 보내거나, 파일을 클라우드 동기화 폴더에 저장하면 콘텐츠는 사용자의 작업에 따라 해당 서비스로 전달되며 해당 서비스의 개인정보 처리방침이 적용됩니다.",
    "1. 系统权限": "1. 시스템 권한",
    "屏幕录制：": "화면 녹화:",
    "用于截屏、长截图与录屏。": "캡처, 스크롤 캡처, 녹화에 사용됩니다.",
    "系统声音：": "시스템 음성:",
    "在你启用电脑声音录制时写入本地视频。": "컴퓨터 음성 녹음을 활성화했을 때 로컬 영상에 기록됩니다.",
    "麦克风：": "마이크:",
    "在你开启麦克风录制时申请，用于录制声音。": "마이크 녹음을 활성화할 때만 요청되며 음성 녹음에 사용됩니다.",
    "摄像头：": "카메라:",
    "在你开启摄像头画面时申请，用于画中画。": "카메라 오버레이를 활성화할 때만 요청되며 PIP에 사용됩니다.",
    "你可以在 macOS「系统设置 → 隐私与安全性」中管理权限。拒绝或撤销权限会影响对应功能。全局快捷键不要求额外开启辅助功能；在 Finder 中显示文件不要求自动化权限。":
        "macOS의 「시스템 설정 → 개인 정보 보호 및 보안」에서 권한을 관리할 수 있습니다. 권한을 거부하거나 취소하면 해당 기능에 영향을 줍니다. 전역 단축키는 접근성 권한을 요구하지 않으며, Finder에서 파일 표시는 자동화 권한을 요구하지 않습니다.",
    "2. 文件、设置与本地日志": "2. 파일, 설정, 로컬 로그",
    "截图与录屏通过保存对话框导出到你选择的位置。录屏过程文件保存在应用支持目录的 SnipX/Recovery 中；本地诊断日志保存在 Library/Logs/SnipX/CrashLogs 中。沙盒版的这些应用目录位于 macOS 为 SnipX 分配的容器内，开发测试版也可能使用项目旁的 CrashLogs 目录。":
        "캡처와 녹화는 저장 대화상자를 통해 사용자가 선택한 위치로 내보냅니다. 진행 중인 녹화 파일은 앱 지원 디렉터리의 SnipX/Recovery에 저장되고, 로컬 진단 로그는 Library/Logs/SnipX/CrashLogs에 저장됩니다. 샌드박스 버전의 이 디렉터리는 macOS가 SnipX에 할당한 컨테이너 안에 있으며, 개발 빌드는 프로젝트 옆의 CrashLogs 디렉터리를 사용할 수도 있습니다.",
    "应用在本机保存快捷键等偏好设置，并检查可用磁盘空间以保护录制文件。这些信息不会自动发送给开发者。OCR 使用 Apple Vision 框架在本机完成，不向服务器上传图片或识别结果。":
        "앱은 단축키 등 설정을 로컬에 저장하고 녹화 파일 보호를 위해 사용 가능한 디스크 공간을 확인합니다. 이 정보는 자동으로 개발자에게 전송되지 않습니다. OCR은 Apple Vision 프레임워크로 로컬에서 실행되며 이미지나 인식 결과가 서버로 업로드되지 않습니다.",
    "删除应用本身不保证删除已导出文件、恢复文件和日志。请先保存需要保留的内容，再自行清理不需要的文件；不要在录制过程中删除恢复文件。":
        "앱 삭제는 내보낸 파일, 복구 파일, 로그의 삭제를 보장하지 않습니다. 보존할 내용은 먼저 저장한 다음 필요 없는 파일은 직접 정리하세요. 녹화 진행 중에는 복구 파일을 삭제하지 마세요.",
    "3. 购买与恢复购买": "3. 구매 및 구매 복구",
    "SnipX Pro 为一次性买断的非消耗型内购，价格以 App 内和 Apple 购买确认界面为准。商品加载、购买、恢复及交易状态同步通过 Apple StoreKit 服务完成，可能需要联网。":
        "SnipX Pro는 일회성 구매의 비소모성 인앱 구매로, 가격은 앱 내 및 Apple 구매 확인 화면에 따릅니다. 상품 로드, 구매, 복구, 거래 상태 동기화는 Apple StoreKit 서비스를 통해 처리되며 인터넷 연결이 필요할 수 있습니다.",
    "Apple 处理付款。SnipX 在本机验证 Apple 提供的交易及权益信息，以决定是否解锁录屏和 GIF。开发者不通过应用收集你的银行卡或支付账户信息。Apple 对其处理的信息适用":
        "결제는 Apple이 처리합니다. SnipX는 Apple이 제공한 거래 및 자격 정보를 로컬에서 검증해 녹화와 GIF 잠금 해제 여부를 결정합니다. 개발자는 앱을 통해 사용자의 카드 또는 결제 계정 정보를 수집하지 않습니다. Apple이 처리하는 정보에는",
    "Apple 隐私政策": "Apple의 개인정보 처리방침이 적용됩니다",
    "4. 主动联系支持与访问官网": "4. 지원팀 능동적 연락 및 공식 사이트 방문",
    "你主动发送邮件时，我们会收到你提供的邮箱、问题描述及附件，仅用于回复和排查问题。请勿发送无关的个人信息、密码或敏感截图；可以联系下方邮箱请求删除你提供的反馈材料。":
        "사용자가 능동적으로 이메일을 보내면 제공된 이메일 주소, 문제 설명 및 첨부 파일을 받으며, 이는 회신 및 문제 조사에만 사용됩니다. 관련 없는 개인정보, 비밀번호, 민감한 스크린샷은 보내지 마세요. 제공한 피드백 자료의 삭제는 아래 이메일로 요청할 수 있습니다.",
    "本站没有加入广告或分析 SDK。网站托管服务可能处理提供页面和保障服务所需的 IP 地址、浏览器请求及访问日志；这与应用在本机处理截图的行为不同。":
        "본 사이트는 광고나 분석 SDK를 포함하지 않습니다. 호스팅 서비스는 페이지 제공과 서비스 유지에 필요한 IP 주소, 브라우저 요청, 접근 로그를 처리할 수 있으며 이는 앱이 캡처를 로컬에서 처리하는 것과는 다릅니다.",
    "5. 政策变更与联系方式": "5. 정책 변경 및 연락처",
    "隐私处理方式变化时，我们会更新本页面及更新日期。隐私问题或删除反馈材料的请求请联系":
        "개인정보 처리 방식이 변경되면 본 페이지와 업데이트 날짜를 갱신합니다. 개인정보 관련 질문이나 피드백 자료 삭제 요청은 다음으로 연락하세요",
    "使用说明见": "사용 안내는",
    "支持与帮助": "지원",
    # support
    "Support": "Support",
    "SnipX 支持与帮助": "SnipX 지원",
    "FAQ、权限引导、反馈渠道 · 适用于 SnipX 1.0.0 及以上版本":
        "FAQ, 권한 안내, 피드백 채널 · SnipX 1.0.0 이상 버전 기준",
    "系统要求": "시스템 요구 사항",
    "macOS 14.0 Sonoma 或更高版本": "macOS 14.0 Sonoma 이상",
    "支持 Apple Silicon（M1 / M2 / M3 / M4）与 Intel Mac": "Apple Silicon (M1 / M2 / M3 / M4) 및 Intel Mac 지원",
    "通用构建（Universal 2）同时包含": "Universal 2 빌드는 다음 두 가지 모두 포함",
    "截图、录屏与 OCR 在本机处理；商品加载、购买与恢复可能需要联网。":
        "캡처, 녹화, OCR은 Mac에서 처리되며 상품 로드, 구매, 복구에는 인터넷 연결이 필요할 수 있습니다.",
    "首次启动：权限引导": "최초 실행: 권한 안내",
    "SnipX 只会在你实际使用对应功能时申请系统权限，遵循 macOS 默认流程，不会启动即弹窗。":
        "SnipX는 해당 기능을 실제로 사용할 때만 시스템 권한을 요청하며 macOS 기본 흐름을 따르고 실행 직후 팝업을 띄우지 않습니다.",
    "首次截屏或录屏时系统会弹窗。授权后到「系统设置 → 隐私与安全性 → 屏幕录制」可看到 SnipX。":
        "최초 캡처 또는 녹화 시 시스템이 팝업을 띄웁니다. 허용 후 「시스템 설정 → 개인 정보 보호 및 보안 → 화면 녹화」에서 SnipX를 확인할 수 있습니다.",
    "仅在你开启「录制麦克风」开关时申请。": "마이크 녹음을 활성화했을 때만 요청됩니다.",
    "仅在你开启「录制摄像头」开关时申请。": "카메라 캡처를 활성화했을 때만 요청됩니다.",
    "录制电脑声音时，按 macOS 的屏幕与系统音频录制权限提示操作。":
        "컴퓨터 음성을 녹음할 때는 macOS의 화면 및 시스템 음성 녹화 권한 안내를 따르세요.",
    "如果误点了「拒绝」，可以到「系统设置 → 隐私与安全性」手动开启；SnipX 内置的「权限」面板也会引导你跳转到对应位置。":
        "실수로 「허용하지 않음」을 선택했다면 「시스템 설정 → 개인 정보 보호 및 보안」에서 수동으로 활성화할 수 있습니다. SnipX 내장 「권한」 패널이 해당 위치로 안내해 줍니다.",
    "Q1：SnipX 联网吗？会上传我的截图吗？": "Q1: SnipX는 인터넷에 연결되나요? 내 캡처를 업로드하나요?",
    "截图、录屏、OCR 与标注在本机处理，不会自动上传给开发者。购买与恢复通过 Apple 服务完成，可能需要联网；主动分享或发邮件时，内容按你的操作交给相应服务。":
        "캡처, 녹화, OCR, 주석은 로컬에서 처리되며 개발자에게 자동으로 업로드되지 않습니다. 구매와 복구는 Apple 서비스를 통해 처리되며 인터넷 연결이 필요할 수 있고, 능동적 공유나 이메일 발신 시 콘텐츠는 사용자의 작업에 따라 해당 서비스로 전달됩니다.",
    "Q2：SnipX Pro 是什么？哪些功能需要付费？": "Q2: SnipX Pro란? 어떤 기능이 유료인가요?",
    "截屏、标注、长截图、置顶、复制、保存、分享等基础功能永久免费。": "캡처, 주석, 스크롤 캡처, 고정하기, 복사, 저장, 공유 등 기본 기능은 영구 무료입니다.",
    "（一次性买断，价格以 Apple 购买界面为准）": "(일회성 구매, 가격은 Apple 구매 화면 기준)",
    "解锁：": "잠금 해제 시 제공:",
    "MP4 录屏（选定区域 / 显示器）": "MP4 녹화 (선정 영역 / 디스플레이)",
    "GIF 录制": "GIF 녹화",
    "系统声音 + 麦克风同时录制": "시스템 음성 + 마이크 동시 녹음",
    "摄像头画中画": "카메라 PIP",
    "倒计时与异常自动恢复": "카운트다운 및 비정상 자동 복구",
    "头尾裁剪导出": "머리/꼬리 잘라 내보내기",
    "Q3：如何恢复购买？": "Q3: 구매를 복구하려면 어떻게 하나요?",
    "打开 SnipX → 菜单栏 → 设置 → 录屏 → 付费墙卡底部「恢复购买」按钮。App 会通过 StoreKit 2 重新校验你的购买状态。":
        "SnipX 실행 → 메뉴바 → 설정 → 녹화 → 페이월 카드 하단 「구매 복구」 버튼을 누르세요. 앱이 StoreKit 2로 구매 상태를 재검증합니다.",
    "Q4：可以更换已授权的功能吗？": "Q4: 이미 활성화된 기능을 변경할 수 있나요?",
    "截屏、标注、长截图的快捷键都可以在「设置 → 快捷键」中自定义，冲突时会自动提示。":
        "캡처, 주석, 스크롤 캡처의 단축키는 「설정 → 단축키」에서 사용자 지정할 수 있으며 충돌 시 자동으로 경고합니다.",
    "Q5：为什么我截不到 SnipX 自己的窗口？": "Q5: 왜 SnipX 자체 창은 캡처되지 않나요?",
    "SnipX 在录屏与截屏时会自动排除自身的菜单栏蒙层、操作浮层与录屏浮动条，避免污染画面。其他 SnipX 窗口（如设置、编辑录屏）默认会被正常捕获。":
        "SnipX는 녹화 및 캡처 시 자체 메뉴바 오버레이, 작업 팝오버, 녹화 플로팅 바를 자동으로 제외해 화면을 깨끗하게 유지합니다. 그 외 SnipX 창(설정, 녹화 편집기 등)은 정상적으로 캡처됩니다.",
    "Q6：OCR 支持哪些语言？": "Q6: OCR은 어떤 언어를 지원하나요?",
    "1.0.0 起，OCR 支持中文（简/繁）、英文及中英混合文本，由 Apple Vision 框架在本地完成识别，无网络依赖。":
        "1.0.0부터 OCR은 간체/번체 중국어, 영어 및 중영 혼합 텍스트를 지원하며 Apple Vision 프레임워크로 로컬에서 인식되어 네트워크에 의존하지 않습니다.",
    "Q7：录屏文件保存在哪里？": "Q7: 녹화 파일은 어디에 저장되나요?",
    "通过保存对话框导出到你选择的位置。录制过程文件保存在应用支持目录的 SnipX/Recovery 中，沙盒版位于 SnipX 的 macOS 容器内。应用会保留可恢复文件；退出前请先保存需要的内容。":
        "저장 대화상자를 통해 사용자가 선택한 위치로 내보냅니다. 진행 중인 녹화 파일은 앱 지원 디렉터리의 SnipX/Recovery에 저장되며, 샌드박스 버전은 SnipX의 macOS 컨테이너 안에 있습니다. 앱은 복구 가능한 파일을 보존하므로 종료 전에 필요한 내용을 먼저 저장하세요.",
    "反馈与问题上报": "피드백 및 버그 신고",
    "如果你遇到 bug、有功能建议或希望贡献想法：": "버그를 발견했거나 기능 제안, 아이디어를 공유하고 싶다면:",
    "邮箱：": "이메일:",
    "请附上：macOS 版本、SnipX 版本、复现步骤、必要时附截图或录屏":
        "다음 정보를 함께 보내주세요: macOS 버전, SnipX 버전, 재현 단계, 필요 시 스크린샷 또는 녹화",
    "SnipX 在异常退出时会保留崩溃日志到": "SnipX는 비정상 종료 시 크래시 로그를 다음 위치에 보존합니다:",
    "提交问题时一并附上可大幅加快定位": "신고 시 함께 첨부해 주시면 원인 파악이 빨라집니다",
    "版本与更新": "버전 및 업데이트",
    "当前最新版本：": "최신 버전:",
    "完整版本变更说明见": "전체 변경 내역은",
    "相关链接": "관련 링크",
    "产品主页": "제품 홈",
},
"es": {
    # common
    "下载 SnipX": "Descargar SnipX [MT]",
    "主题：跟随系统": "Tema: seguir sistema [MT]",
    "主题：浅色": "Tema: claro [MT]",
    "主题：深色": "Tema: oscuro [MT]",
    "特性": "Características [MT]",
    "下载": "Descargar [MT]",
    "关于": "Acerca de [MT]",
    "查看功能": "Ver funciones [MT]",
    "主页": "Inicio [MT]",
    "支持": "Soporte [MT]",
    "隐私政策": "Política de privacidad [MT]",
    "© 2026 SnipX. All rights reserved.": "© 2026 SnipX. All rights reserved.",
    # hero
    "macOS 14+ · 原生应用": "macOS 14+ · App nativa [MT]",
    "Mac 截屏与录屏，一触即达。": "Captura y grabación de pantalla en Mac, a un toque. [MT]",
    "原生 AppKit + Swift + ScreenCaptureKit。物理像素输出、本地 OCR、可编辑快捷键、长截图拼接、本地 MP4 录制。内容在本机处理，无需注册 SnipX 账号。":
        "AppKit + Swift + ScreenCaptureKit nativos. Salida en píxeles físicos, OCR local, atajos editables, capturas largas con unión automática, grabación MP4 local. El contenido se procesa en tu Mac, sin cuenta de SnipX. [MT]",
    "macOS 14+": "macOS 14+",
    "Universal 2 · Apple Silicon + Intel": "Universal 2 · Apple Silicon + Intel",
    "本地 OCR": "OCR local [MT]",
    "SnipX Pro 录屏/GIF": "SnipX Pro grabación/GIF [MT]",
    "下载 SnipX": "Descargar SnipX [MT]",
    # features
    "菜单栏常驻，所见即可截": "Siempre en la barra de menús [MT]",
    "截屏、标注、录屏、长截图，全部在菜单栏一触即达。": "Captura, anotación, grabación y captura larga, todo desde la barra de menús en un toque. [MT]",
    "常驻菜单栏": "Reside en la barra de menús [MT]",
    "点击即开，不打扰": "Un toque para abrir, sin estorbar [MT]",
    "SnipX 始终浮于屏幕角落的菜单栏。无需打开主窗口，点击即弹出截屏 / 录屏入口。":
        "SnipX permanece en la esquina de la barra de menús. Sin ventana principal: un toque revela las entradas de captura / grabación. [MT]",
    "截屏、录屏、标注、设置 全部直达": "Captura, grabación, anotación y ajustes a un toque [MT]",
    "不抢焦点、不打扰当前工作": "No roba el foco ni interrumpe tu trabajo [MT]",
    "原生菜单栏图标，遵循 macOS 设计语言": "Icono nativo en la barra de menús, siguiendo el diseño de macOS [MT]",
    "可编辑快捷键": "Atajos editables [MT]",
    "全局快捷键，自由绑定": "Atajos globales configurables libremente [MT]",
    "截屏、录屏、标注、长截图 — 每个动作都可绑定独立快捷键，避免与其他应用冲突。":
        "Captura, grabación, anotación y captura larga: cada acción tiene su propio atajo, con avisos si hay conflicto. [MT]",
    "支持单键 / 组合键 / 修饰键": "Soporta tecla única / combinaciones / modificadores [MT]",
    "冲突检测，一键恢复默认": "Detección de conflictos y restauración con un toque [MT]",
    "录屏、截屏独立绑定，标注即时唤起": "Atajos independientes para grabación y captura, anotación al instante [MT]",
    "四类截屏": "Cuatro modos de captura [MT]",
    "区域 / 窗口 / 全屏 / 长截图": "Región / ventana / pantalla completa / captura larga [MT]",
    "物理像素输出，自动按显示器倍率渲染。窗口截屏自动识别应用窗口边缘，长截图无缝拼接。":
        "Salida en píxeles físicos, renderizada según la escala de tu pantalla. La captura de ventana detecta automáticamente los bordes; la captura larga se une sin costuras. [MT]",
    "区域截屏：拖拽选区，物理像素精度": "Captura de región: arrastra para seleccionar, precisión de píxel [MT]",
    "窗口截屏：自动选窗，背景透明": "Captura de ventana: selección automática, fondo transparente [MT]",
    "全屏截屏：多显示器同时输出": "Pantalla completa: varias pantallas a la vez [MT]",
    "长截图：滚动拼接，自动对齐": "Captura larga: unión automática sin costuras [MT]",
    "本地 OCR（1.0.0 新增）": "OCR local (nuevo en 1.0.0) [MT]",
    "截图里的文字，一键识别": "Reconoce el texto de tus capturas con un toque [MT]",
    "基于 Apple Vision 框架，在你的 Mac 上直接识别截图中的中文、英文与中英混合文本。识别结果可编辑、可复制，不上传任何内容。":
        "Con el framework Apple Vision, SnipX reconoce chino, inglés y texto mixto directamente en tu Mac. Edita o copia el resultado; nada se sube. [MT]",
    "中文（简/繁）、英文与中英混排": "Chino simplificado y tradicional, inglés y mixto [MT]",
    "完全本地识别，截图与文字不出本机": "Reconocimiento 100% local, no sale de tu Mac [MT]",
    "识别后可编辑、复制或取消": "Edita, copia o cancela tras reconocer [MT]",
    "适用于截屏后的二次编辑与提取": "Ideal para extraer texto de tus capturas [MT]",
    "标注工具": "Herramientas de anotación [MT]",
    "矩形 / 箭头 / 文字 / 马赛克": "Rectángulo / flecha / texto / mosaico [MT]",
    "截屏后即时标注，所有元素可移动、可删除、可撤销重做。裁剪、马赛克、颜色选择器一应俱全。":
        "Anota al instante tras capturar. Mueve, elimina, deshaz y rehaz. Recorte, mosaico y selector de color integrados. [MT]",
    "矩形、椭圆、箭头、画笔、文字": "Rectángulo, elipse, flecha, pincel, texto [MT]",
    "马赛克模糊敏感信息": "Mosaico para difuminar datos sensibles [MT]",
    "撤销 / 重做 / 裁剪 / 颜色选择器": "Deshacer / rehacer / recortar / selector de color [MT]",
    "本地 MP4 录屏 · SnipX Pro": "Grabación MP4 local · SnipX Pro [MT]",
    "倒计时 · 系统声 + 麦克风 · 自动恢复": "Cuenta atrás · audio del sistema + micrófono · recuperación automática [MT]",
    "基于 ScreenCaptureKit 本地录制，支持同时录制系统声音与麦克风，倒计时、磁盘保护、异常恢复一应俱全。头尾裁剪导出，无需第三方编辑器。":
        "Basado en ScreenCaptureKit para grabar localmente. Captura audio del sistema y micrófono a la vez, con cuenta atrás, protección de disco y recuperación tras cierre inesperado. Recorta inicio y fin sin editores de terceros. [MT]",
    "区域 / 窗口 / 显示器三种录屏模式": "Tres modos: región / ventana / pantalla [MT]",
    "系统声音与麦克风同时录制，单一音轨": "Audio del sistema y micrófono en una sola pista [MT]",
    "倒计时与状态指示，录屏不打断": "Cuenta atrás e indicador en vivo, sin interrumpir [MT]",
    "异常退出后 Recovery 保留录制": "Recovery conserva el clip tras cierre inesperado [MT]",
    "头尾裁剪导出为新 MP4": "Recorta inicio y fin, exporta un nuevo MP4 [MT]",
    "录屏与 GIF 录制需解锁 <strong>SnipX Pro</strong>（一次性买断，价格以 App Store 为准）。截屏、标注、长截图永久免费。":
        "La grabación y la captura GIF requieren SnipX Pro (compra única, precio en el App Store). Captura, anotación y captura larga son gratis para siempre. [MT]",
    "零数据外传": "Cero datos salen de tu Mac [MT]",
    "完全离线运行": "Funciona totalmente sin conexión [MT]",
    "截图、录屏与 OCR 在本机处理，不自动上传内容或遥测。购买与恢复通过 Apple 服务完成。":
        "Captura, grabación y OCR se procesan localmente. No se sube contenido ni telemetría. Las compras y restauraciones pasan por Apple. [MT]",
    "购买与恢复可能需要联网": "Las compras y restauraciones pueden requerir internet [MT]",
    "无账号、无登录、无云同步": "Sin cuenta, sin inicio de sesión, sin sincronización en la nube [MT]",
    "无第三方 SDK、无埋点": "Sin SDK de terceros ni rastreadores [MT]",
    "开源友好的本地存储": "Almacenamiento local, amigable con el código abierto [MT]",
    # install
    "从 Mac App Store 获取": "Descargar del Mac App Store [MT]",
    "在 App Store 一键安装，内购、更新与恢复购买由 Apple 处理。":
        "Instala con un toque desde el App Store. Compras, actualizaciones y restauraciones las gestiona Apple. [MT]",
    "前往 App Store": "Ir al App Store [MT]",
    "点击下方按钮，跳转 Mac App Store 的 SnipX 应用页。": "Toca el botón de abajo para abrir la página de SnipX en el Mac App Store. [MT]",
    "安装并打开": "Instalar y abrir [MT]",
    "点按「获取」安装 SnipX，完成后从「应用程序」或菜单栏打开。":
        "Pulsa \"Obtener\" para instalar SnipX y ábrelo desde Aplicaciones o la barra de menús. [MT]",
    "授权系统权限": "Conceder permisos del sistema [MT]",
    "按所用功能授权：屏幕录制、系统声音、麦克风和摄像头。":
        "Autoriza por función: grabación de pantalla, audio del sistema, micrófono y cámara. [MT]",
    "前往 App Store 下载": "Descargar desde el App Store [MT]",
    "App Store 应用页即将上线，链接待回填。": "La ficha del App Store estará disponible pronto. El enlace se añadirá cuando esté listo. [MT]",
    "macOS 14+ · Universal 2（Apple Silicon + Intel）· 仅 3 MB":
        "macOS 14+ · Universal 2 (Apple Silicon + Intel) · solo 3 MB [MT]",
    "基础截屏永久免费 · 录屏与 GIF 录制需 <a href=\"./#about\">SnipX Pro</a>（一次性买断）":
        "Captura básica gratis para siempre · grabación y GIF requieren SnipX Pro (compra única) [MT]",
    # about
    "关于 SnipX": "Acerca de SnipX [MT]",
    "原生开发": "Desarrollo nativo [MT]",
    "Swift + AppKit + SwiftUI + ScreenCaptureKit + AVFoundation + Carbon 编写，无 WebView、无 Electron、无包装层。":
        "Escrito en Swift + AppKit + SwiftUI + ScreenCaptureKit + AVFoundation + Carbon. Sin WebView, sin Electron, sin capas envolventes. [MT]",
    "隐私优先": "Privacidad primero [MT]",
    "内容处理在本机，无需注册 SnipX 账号。购买由 Apple 处理；主动分享由你选择。详见":
        "Todo el procesamiento queda en tu Mac, sin cuenta de SnipX. Las compras pasan por Apple; compartir es siempre tu decisión. Más detalles en [MT]",
    "SnipX Pro": "SnipX Pro [MT]",
    "截屏、标注、长截图、置顶永久免费。一次性买断解锁 MP4 录屏与 GIF 录制，价格以 App Store 为准。":
        "Captura, anotación, captura larga y fijado son gratis para siempre. Una compra única desbloquea grabación MP4 y captura GIF. Precio fijado en el App Store. [MT]",
    "持续维护": "Mantenimiento continuo [MT]",
    "当前版本": "Versión actual [MT]",
    "每个版本均经过手测、单元测试、功能测试三道关。需要帮助？":
        "Cada versión pasa por pruebas manuales, unitarias y funcionales. ¿Necesitas ayuda? [MT]",
    "支持页": "página de soporte [MT]",
    # footer
    "当前版本 1.0.0": "Versión actual 1.0.0 [MT]",
    # images alt
    "SnipX 界面预览": "Vista previa de la interfaz de SnipX [MT]",
    "SnipX 菜单栏截屏入口": "Entrada de captura de SnipX en la barra de menús [MT]",
    "SnipX 全局快捷键设置": "Configuración de atajos globales de SnipX [MT]",
    "SnipX 区域 / 窗口 / 全屏 / 长截图": "SnipX región / ventana / pantalla completa / captura larga [MT]",
    "SnipX 本地 OCR 识别截图文字": "OCR local de SnipX reconoce texto de capturas [MT]",
    "SnipX 标注工具": "Herramientas de anotación de SnipX [MT]",
    "SnipX MP4 录屏": "Grabación MP4 de SnipX [MT]",
    "SnipX 完全离线运行": "SnipX funciona totalmente sin conexión [MT]",
    # privacy
    "Privacy Policy": "Privacy Policy",
    "SnipX 隐私政策": "Política de privacidad de SnipX [MT]",
    "最后更新：2026 年 9 月 6 日 · 适用于 SnipX macOS 应用与本站": "Última actualización: 6 de septiembre de 2026 · se aplica a la app SnipX para macOS y a este sitio web [MT]",
    "内容在本机处理": "El contenido se procesa en el dispositivo [MT]",
    "截图、录屏、声音、摄像头画面、OCR 识别结果和标注均在你的 Mac 上处理。SnipX 不会自动把这些内容或本地诊断日志上传给开发者，不集成广告、追踪或第三方分析 SDK。":
        "Capturas, grabaciones, audio, vídeo de cámara, resultados de OCR y anotaciones se procesan en tu Mac. SnipX no sube tu contenido ni registros de diagnóstico locales, ni integra anuncios, rastreadores ni SDKs de terceros. [MT]",
    "当你主动使用系统分享、发送反馈或将文件保存到云盘同步目录时，内容会按你的操作交给相应服务，其处理方式适用该服务的隐私政策。":
        "Cuando compartes, envías comentarios o guardas archivos en una carpeta sincronizada en la nube, el contenido pasa al servicio correspondiente según tu acción y se aplica su política de privacidad. [MT]",
    "1. 系统权限": "1. Permisos del sistema [MT]",
    "屏幕录制：": "Grabación de pantalla: [MT]",
    "用于截屏、长截图与录屏。": "necesaria para captura, captura larga y grabación. [MT]",
    "系统声音：": "Audio del sistema: [MT]",
    "在你启用电脑声音录制时写入本地视频。": "se escribe en el vídeo local al activar la captura de audio del ordenador. [MT]",
    "麦克风：": "Micrófono: [MT]",
    "在你开启麦克风录制时申请，用于录制声音。": "se solicita solo al activar la captura de micrófono. [MT]",
    "摄像头：": "Cámara: [MT]",
    "在你开启摄像头画面时申请，用于画中画。": "se solicita solo al activar la superposición de cámara (picture-in-picture). [MT]",
    "你可以在 macOS「系统设置 → 隐私与安全性」中管理权限。拒绝或撤销权限会影响对应功能。全局快捷键不要求额外开启辅助功能；在 Finder 中显示文件不要求自动化权限。":
        "Gestiona los permisos en Ajustes del Sistema → Privacidad y seguridad de macOS. Denegar o revocar un permiso desactiva la función correspondiente. Los atajos globales no requieren Accesibilidad; mostrar archivos en Finder no requiere Automatización. [MT]",
    "2. 文件、设置与本地日志": "2. Archivos, ajustes y registros locales [MT]",
    "截图与录屏通过保存对话框导出到你选择的位置。录屏过程文件保存在应用支持目录的 SnipX/Recovery 中；本地诊断日志保存在 Library/Logs/SnipX/CrashLogs 中。沙盒版的这些应用目录位于 macOS 为 SnipX 分配的容器内，开发测试版也可能使用项目旁的 CrashLogs 目录。":
        "Las capturas y grabaciones se exportan mediante un diálogo a la ubicación que elijas. Las grabaciones en curso se guardan en SnipX/Recovery dentro del directorio de soporte de la app; los registros diagnósticos locales van a Library/Logs/SnipX/CrashLogs. En la versión sandbox estas carpetas están dentro del contenedor asignado por macOS a SnipX; la versión de desarrollo puede usar una carpeta CrashLogs junto al proyecto. [MT]",
    "应用在本机保存快捷键等偏好设置，并检查可用磁盘空间以保护录制文件。这些信息不会自动发送给开发者。OCR 使用 Apple Vision 框架在本机完成，不向服务器上传图片或识别结果。":
        "La app guarda localmente ajustes como los atajos y comprueba el espacio en disco para proteger las grabaciones. Estos datos no se envían automáticamente al desarrollador. El OCR se ejecuta en el dispositivo con Apple Vision; las imágenes y resultados nunca llegan a un servidor. [MT]",
    "删除应用本身不保证删除已导出文件、恢复文件和日志。请先保存需要保留的内容，再自行清理不需要的文件；不要在录制过程中删除恢复文件。":
        "Desinstalar la app no garantiza el borrado de archivos exportados, archivos de recuperación ni registros. Guarda primero lo que quieras conservar y luego limpia lo que no necesites. No borres archivos de recuperación durante una grabación. [MT]",
    "3. 购买与恢复购买": "3. Compras y restauración [MT]",
    "SnipX Pro 为一次性买断的非消耗型内购，价格以 App 内和 Apple 购买确认界面为准。商品加载、购买、恢复及交易状态同步通过 Apple StoreKit 服务完成，可能需要联网。":
        "SnipX Pro es una compra in-app no consumible de un solo pago. El precio se muestra en la app y en la confirmación de compra de Apple. La carga del producto, compra, restauración y sincronización del estado de la transacción pasan por StoreKit de Apple y pueden requerir internet. [MT]",
    "Apple 处理付款。SnipX 在本机验证 Apple 提供的交易及权益信息，以决定是否解锁录屏和 GIF。开发者不通过应用收集你的银行卡或支付账户信息。Apple 对其处理的信息适用":
        "Apple gestiona los pagos. SnipX verifica localmente la transacción y los datos de derecho que Apple proporciona para decidir si desbloquea grabación y GIF. El desarrollador no recoge datos de tarjeta ni de cuenta de pago a través de la app. Para la información que Apple trata, [MT]",
    "Apple 隐私政策": "se aplica la Política de privacidad de Apple [MT]",
    "4. 主动联系支持与访问官网": "4. Contactar con soporte y visitar el sitio [MT]",
    "你主动发送邮件时，我们会收到你提供的邮箱、问题描述及附件，仅用于回复和排查问题。请勿发送无关的个人信息、密码或敏感截图；可以联系下方邮箱请求删除你提供的反馈材料。":
        "Cuando nos escribes, recibimos el correo, la descripción del problema y los adjuntos que envíes, que usamos solo para responder y depurar. No envíes datos personales no relacionados, contraseñas ni capturas sensibles. Puedes escribir a la dirección de abajo para solicitar la eliminación del material que proporcionaste. [MT]",
    "本站没有加入广告或分析 SDK。网站托管服务可能处理提供页面和保障服务所需的 IP 地址、浏览器请求及访问日志；这与应用在本机处理截图的行为不同。":
        "Este sitio no incluye anuncios ni SDKs de análisis. El proveedor de hosting puede procesar direcciones IP, peticiones del navegador y registros de acceso necesarios para servir y asegurar el sitio, algo distinto del procesamiento local de capturas en la app. [MT]",
    "5. 政策变更与联系方式": "5. Cambios y contacto [MT]",
    "隐私处理方式变化时，我们会更新本页面及更新日期。隐私问题或删除反馈材料的请求请联系":
        "Si cambian nuestras prácticas de privacidad, actualizaremos esta página y su fecha. Para preguntas de privacidad o solicitudes de eliminación de material de feedback, escribe a [MT]",
    "使用说明见": "Las instrucciones de uso están en [MT]",
    "支持与帮助": "Soporte y ayuda [MT]",
    # support
    "Support": "Support",
    "SnipX 支持与帮助": "Soporte de SnipX [MT]",
    "FAQ、权限引导、反馈渠道 · 适用于 SnipX 1.0.0 及以上版本":
        "FAQ, guía de permisos y canales de feedback · para SnipX 1.0.0 y posteriores [MT]",
    "系统要求": "Requisitos del sistema [MT]",
    "macOS 14.0 Sonoma 或更高版本": "macOS 14.0 Sonoma o posterior [MT]",
    "支持 Apple Silicon（M1 / M2 / M3 / M4）与 Intel Mac": "Compatible con Apple Silicon (M1 / M2 / M3 / M4) y Mac Intel [MT]",
    "通用构建（Universal 2）同时包含": "La compilación Universal 2 incluye ambas [MT]",
    "截图、录屏与 OCR 在本机处理；商品加载、购买与恢复可能需要联网。":
        "Captura, grabación y OCR se procesan en el dispositivo; la carga del producto, compra y restauración pueden requerir internet. [MT]",
    "首次启动：权限引导": "Primer inicio: guía de permisos [MT]",
    "SnipX 只会在你实际使用对应功能时申请系统权限，遵循 macOS 默认流程，不会启动即弹窗。":
        "SnipX solo pide permisos del sistema cuando usas realmente la función correspondiente, siguiendo el flujo por defecto de macOS, sin avisos al iniciar. [MT]",
    "首次截屏或录屏时系统会弹窗。授权后到「系统设置 → 隐私与安全性 → 屏幕录制」可看到 SnipX。":
        "macOS mostrará un aviso en tu primera captura o grabación. Tras concederlo, verás SnipX en Ajustes del Sistema → Privacidad y seguridad → Grabación de pantalla. [MT]",
    "仅在你开启「录制麦克风」开关时申请。": "Se solicita solo al activar la captura de micrófono. [MT]",
    "仅在你开启「录制摄像头」开关时申请。": "Se solicita solo al activar la captura de cámara. [MT]",
    "录制电脑声音时，按 macOS 的屏幕与系统音频录制权限提示操作。":
        "Para capturar el audio del ordenador, sigue el aviso de permiso de pantalla y audio del sistema de macOS. [MT]",
    "如果误点了「拒绝」，可以到「系统设置 → 隐私与安全性」手动开启；SnipX 内置的「权限」面板也会引导你跳转到对应位置。":
        "Si pulsaste \"No permitir\" por error, puedes activarlo manualmente en Ajustes del Sistema → Privacidad y seguridad. El panel \"Permisos\" integrado en SnipX también te lleva al sitio correcto. [MT]",
    "Q1：SnipX 联网吗？会上传我的截图吗？": "P1: ¿SnipX se conecta a internet? ¿Sube mis capturas? [MT]",
    "截图、录屏、OCR 与标注在本机处理，不会自动上传给开发者。购买与恢复通过 Apple 服务完成，可能需要联网；主动分享或发邮件时，内容按你的操作交给相应服务。":
        "Captura, grabación, OCR y anotación se procesan en el dispositivo y nunca se suben al desarrollador. Las compras y restauraciones pasan por Apple y pueden requerir internet. Si compartes o envías por correo, el contenido se entrega al servicio correspondiente según tu acción. [MT]",
    "Q2：SnipX Pro 是什么？哪些功能需要付费？": "P2: ¿Qué es SnipX Pro? ¿Qué funciones son de pago? [MT]",
    "截屏、标注、长截图、置顶、复制、保存、分享等基础功能永久免费。": "Captura, anotación, captura larga, fijado, copiar, guardar, compartir y otras funciones básicas son gratis para siempre. [MT]",
    "（一次性买断，价格以 Apple 购买界面为准）": "(compra única, precio fijado por Apple) [MT]",
    "解锁：": "desbloquea: [MT]",
    "MP4 录屏（选定区域 / 显示器）": "Grabación MP4 (región / pantalla seleccionada) [MT]",
    "GIF 录制": "Captura GIF [MT]",
    "系统声音 + 麦克风同时录制": "Audio del sistema + micrófono a la vez [MT]",
    "摄像头画中画": "Cámara picture-in-picture [MT]",
    "倒计时与异常自动恢复": "Cuenta atrás y recuperación tras cierre inesperado [MT]",
    "头尾裁剪导出": "Recortar inicio y fin y exportar [MT]",
    "Q3：如何恢复购买？": "P3: ¿Cómo restauro una compra? [MT]",
    "打开 SnipX → 菜单栏 → 设置 → 录屏 → 付费墙卡底部「恢复购买」按钮。App 会通过 StoreKit 2 重新校验你的购买状态。":
        "Abre SnipX → barra de menús → Ajustes → Grabación → pulsa \"Restaurar compra\" en la parte inferior de la tarjeta de pago. La app revalidará tu estado de compra mediante StoreKit 2. [MT]",
    "Q4：可以更换已授权的功能吗？": "P4: ¿Puedo cambiar una función ya autorizada? [MT]",
    "截屏、标注、长截图的快捷键都可以在「设置 → 快捷键」中自定义，冲突时会自动提示。":
        "Los atajos de captura, anotación y captura larga se personalizan en Ajustes → Atajos, con avisos automáticos ante conflictos. [MT]",
    "Q5：为什么我截不到 SnipX 自己的窗口？": "P5: ¿Por qué no puedo capturar la propia ventana de SnipX? [MT]",
    "SnipX 在录屏与截屏时会自动排除自身的菜单栏蒙层、操作浮层与录屏浮动条，避免污染画面。其他 SnipX 窗口（如设置、编辑录屏）默认会被正常捕获。":
        "Durante la captura o grabación, SnipX excluye automáticamente sus propios overlays de barra de menús, popovers de acción y barra flotante de grabación para mantener la imagen limpia. Otras ventanas de SnipX (Ajustes, editor de grabación, etc.) se capturan con normalidad. [MT]",
    "Q6：OCR 支持哪些语言？": "P6: ¿Qué idiomas admite el OCR? [MT]",
    "1.0.0 起，OCR 支持中文（简/繁）、英文及中英混合文本，由 Apple Vision 框架在本地完成识别，无网络依赖。":
        "Desde 1.0.0, el OCR admite chino simplificado y tradicional, inglés y texto mixto chino/inglés, todo reconocido en el dispositivo con el framework Apple Vision, sin depender de la red. [MT]",
    "Q7：录屏文件保存在哪里？": "P7: ¿Dónde se guardan mis grabaciones? [MT]",
    "通过保存对话框导出到你选择的位置。录制过程文件保存在应用支持目录的 SnipX/Recovery 中，沙盒版位于 SnipX 的 macOS 容器内。应用会保留可恢复文件；退出前请先保存需要的内容。":
        "Se exportan mediante un diálogo a la ubicación que elijas. Los archivos en curso se guardan en SnipX/Recovery dentro del directorio de soporte de la app (en el contenedor de macOS para la versión sandbox). La app conserva archivos recuperables; guarda lo necesario antes de salir. [MT]",
    "反馈与问题上报": "Comentarios e informes de errores [MT]",
    "如果你遇到 bug、有功能建议或希望贡献想法：": "Si encuentras un bug, tienes una idea de función o quieres aportar: [MT]",
    "邮箱：": "Correo: [MT]",
    "请附上：macOS 版本、SnipX 版本、复现步骤、必要时附截图或录屏":
        "Adjunta: versión de macOS, versión de SnipX, pasos para reproducir y, si es posible, una captura o grabación [MT]",
    "SnipX 在异常退出时会保留崩溃日志到": "SnipX conserva los registros de cierre en [MT]",
    "提交问题时一并附上可大幅加快定位": "adjuntarlos acelera mucho el diagnóstico [MT]",
    "版本与更新": "Versiones y actualizaciones [MT]",
    "当前最新版本：": "Versión más reciente: [MT]",
    "完整版本变更说明见": "Las notas completas están en [MT]",
    "相关链接": "Enlaces relacionados [MT]",
    "产品主页": "Página del producto [MT]",
},
"pt": {
    # common
    "下载 SnipX": "Baixar SnipX [MT]",
    "主题：跟随系统": "Tema: seguir sistema [MT]",
    "主题：浅色": "Tema: claro [MT]",
    "主题：深色": "Tema: escuro [MT]",
    "特性": "Recursos [MT]",
    "下载": "Baixar [MT]",
    "关于": "Sobre [MT]",
    "查看功能": "Ver recursos [MT]",
    "主页": "Início [MT]",
    "支持": "Suporte [MT]",
    "隐私政策": "Política de privacidade [MT]",
    "© 2026 SnipX. All rights reserved.": "© 2026 SnipX. All rights reserved.",
    # hero
    "macOS 14+ · 原生应用": "macOS 14+ · App nativa [MT]",
    "Mac 截屏与录屏，一触即达。": "Captura e gravação de tela no Mac, com um toque. [MT]",
    "原生 AppKit + Swift + ScreenCaptureKit。物理像素输出、本地 OCR、可编辑快捷键、长截图拼接、本地 MP4 录制。内容在本机处理，无需注册 SnipX 账号。":
        "AppKit + Swift + ScreenCaptureKit nativos. Saída em pixels físicos, OCR local, atalhos editáveis, captura de rolagem, gravação MP4 local. Tudo é processado no seu Mac, sem conta SnipX. [MT]",
    "macOS 14+": "macOS 14+",
    "Universal 2 · Apple Silicon + Intel": "Universal 2 · Apple Silicon + Intel",
    "本地 OCR": "OCR local [MT]",
    "SnipX Pro 录屏/GIF": "SnipX Pro gravação/GIF [MT]",
    "下载 SnipX": "Baixar SnipX [MT]",
    # features
    "菜单栏常驻，所见即可截": "Sempre na barra de menus [MT]",
    "截屏、标注、录屏、长截图，全部在菜单栏一触即达。": "Captura, anotação, gravação e captura de rolagem, tudo a partir da barra de menus em um toque. [MT]",
    "常驻菜单栏": "Reside na barra de menus [MT]",
    "点击即开，不打扰": "Toque para abrir, sem atrapalhar [MT]",
    "SnipX 始终浮于屏幕角落的菜单栏。无需打开主窗口，点击即弹出截屏 / 录屏入口。":
        "SnipX fica quieto no canto da barra de menus. Sem janela principal: um toque revela os atalhos de captura e gravação. [MT]",
    "截屏、录屏、标注、设置 全部直达": "Captura, gravação, anotação e ajustes em um toque [MT]",
    "不抢焦点、不打扰当前工作": "Não rouba o foco nem atrapalha seu trabalho [MT]",
    "原生菜单栏图标，遵循 macOS 设计语言": "Ícone nativo na barra de menus, seguindo o design do macOS [MT]",
    "可编辑快捷键": "Atalhos editáveis [MT]",
    "全局快捷键，自由绑定": "Atalhos globais configuráveis livremente [MT]",
    "截屏、录屏、标注、长截图 — 每个动作都可绑定独立快捷键，避免与其他应用冲突。":
        "Captura, gravação, anotação e captura de rolagem: cada ação tem seu próprio atalho, com avisos em caso de conflito. [MT]",
    "支持单键 / 组合键 / 修饰键": "Suporta tecla única / combinações / modificadores [MT]",
    "冲突检测，一键恢复默认": "Detecção de conflitos e restauração com um toque [MT]",
    "录屏、截屏独立绑定，标注即时唤起": "Atalhos independentes para gravação e captura, anotação sob demanda [MT]",
    "四类截屏": "Quatro modos de captura [MT]",
    "区域 / 窗口 / 全屏 / 长截图": "Região / janela / tela cheia / rolagem [MT]",
    "物理像素输出，自动按显示器倍率渲染。窗口截屏自动识别应用窗口边缘，长截图无缝拼接。":
        "Saída em pixels físicos, renderizada automaticamente na escala do seu monitor. A captura de janela detecta as bordas dos apps; a captura de rolagem se une sem emendas. [MT]",
    "区域截屏：拖拽选区，物理像素精度": "Captura de região: arraste para selecionar, precisão de pixel [MT]",
    "窗口截屏：自动选窗，背景透明": "Captura de janela: seleção automática, fundo transparente [MT]",
    "全屏截屏：多显示器同时输出": "Tela cheia: vários monitores ao mesmo tempo [MT]",
    "长截图：滚动拼接，自动对齐": "Rolagem: união automática, sem desalinhamento [MT]",
    "本地 OCR（1.0.0 新增）": "OCR local (novo em 1.0.0) [MT]",
    "截图里的文字，一键识别": "Reconheça texto das suas capturas com um toque [MT]",
    "基于 Apple Vision 框架，在你的 Mac 上直接识别截图中的中文、英文与中英混合文本。识别结果可编辑、可复制，不上传任何内容。":
        "Com o framework Apple Vision, o SnipX reconhece chinês, inglês e texto misto diretamente no seu Mac. Edite ou copie o resultado; nada é enviado. [MT]",
    "中文（简/繁）、英文与中英混排": "Chinês simplificado e tradicional, inglês e misto [MT]",
    "完全本地识别，截图与文字不出本机": "Reconhecimento totalmente local, não sai do seu Mac [MT]",
    "识别后可编辑、复制或取消": "Edite, copie ou cancele após reconhecer [MT]",
    "适用于截屏后的二次编辑与提取": "Ótimo para editar e extrair texto das capturas [MT]",
    "标注工具": "Ferramentas de anotação [MT]",
    "矩形 / 箭头 / 文字 / 马赛克": "Retângulo / seta / texto / mosaico [MT]",
    "截屏后即时标注，所有元素可移动、可删除、可撤销重做。裁剪、马赛克、颜色选择器一应俱全。":
        "Anote no instante da captura. Mova, apague, desfaça e refaça. Recorte, mosaico e seletor de cores integrados. [MT]",
    "矩形、椭圆、箭头、画笔、文字": "Retângulo, elipse, seta, pincel, texto [MT]",
    "马赛克模糊敏感信息": "Mosaico para borrar informações sensíveis [MT]",
    "撤销 / 重做 / 裁剪 / 颜色选择器": "Desfazer / refazer / recortar / seletor de cores [MT]",
    "本地 MP4 录屏 · SnipX Pro": "Gravação MP4 local · SnipX Pro [MT]",
    "倒计时 · 系统声 + 麦克风 · 自动恢复": "Contagem regressiva · áudio do sistema + microfone · recuperação automática [MT]",
    "基于 ScreenCaptureKit 本地录制，支持同时录制系统声音与麦克风，倒计时、磁盘保护、异常恢复一应俱全。头尾裁剪导出，无需第三方编辑器。":
        "Gravação local baseada em ScreenCaptureKit. Capture áudio do sistema e microfone ao mesmo tempo, com contagem regressiva, proteção de disco e recuperação após travamentos. Recorte início e fim e exporte sem editores de terceiros. [MT]",
    "区域 / 窗口 / 显示器三种录屏模式": "Três modos de gravação: região / janela / monitor [MT]",
    "系统声音与麦克风同时录制，单一音轨": "Áudio do sistema + microfone em uma única faixa [MT]",
    "倒计时与状态指示，录屏不打断": "Contagem regressiva e status ao vivo, sem interrupção [MT]",
    "异常退出后 Recovery 保留录制": "Recovery preserva a gravação após queda [MT]",
    "头尾裁剪导出为新 MP4": "Recorte início e fim, exporte um novo MP4 [MT]",
    "录屏与 GIF 录制需解锁 <strong>SnipX Pro</strong>（一次性买断，价格以 App Store 为准）。截屏、标注、长截图永久免费。":
        "Gravação e captura GIF exigem <strong>SnipX Pro</strong> (compra única, preço definido na App Store). Captura, anotação e captura de rolagem são grátis para sempre. [MT]",
    "零数据外传": "Zero dados saindo do seu Mac [MT]",
    "完全离线运行": "Funciona totalmente offline [MT]",
    "截图、录屏与 OCR 在本机处理，不自动上传内容或遥测。购买与恢复通过 Apple 服务完成。":
        "Captura, gravação e OCR são processados localmente. Nada é enviado automaticamente, nem telemetria. Compras e restauração passam pela Apple. [MT]",
    "购买与恢复可能需要联网": "Compras e restauração podem exigir internet [MT]",
    "无账号、无登录、无云同步": "Sem conta, sem login, sem sincronização na nuvem [MT]",
    "无第三方 SDK、无埋点": "Sem SDKs de terceiros nem rastreadores [MT]",
    "开源友好的本地存储": "Armazenamento local, amigável ao código aberto [MT]",
    # install
    "从 Mac App Store 获取": "Obtenha na Mac App Store [MT]",
    "在 App Store 一键安装，内购、更新与恢复购买由 Apple 处理。":
        "Instale com um toque na App Store. Compras, atualizações e restauração são tratadas pela Apple. [MT]",
    "前往 App Store": "Ir para a App Store [MT]",
    "点击下方按钮，跳转 Mac App Store 的 SnipX 应用页。": "Toque no botão abaixo para abrir a página do SnipX na Mac App Store. [MT]",
    "安装并打开": "Instalar e abrir [MT]",
    "点按「获取」安装 SnipX，完成后从「应用程序」或菜单栏打开。":
        "Toque em \"Obter\" para instalar o SnipX e abra depois em Aplicativos ou na barra de menus. [MT]",
    "授权系统权限": "Conceder permissões do sistema [MT]",
    "按所用功能授权：屏幕录制、系统声音、麦克风和摄像头。":
        "Autorize por recurso: gravação de tela, áudio do sistema, microfone e câmera. [MT]",
    "前往 App Store 下载": "Baixar na App Store [MT]",
    "App Store 应用页即将上线，链接待回填。": "A página na App Store será publicada em breve. O link será adicionado quando estiver pronto. [MT]",
    "macOS 14+ · Universal 2（Apple Silicon + Intel）· 仅 3 MB":
        "macOS 14+ · Universal 2 (Apple Silicon + Intel) · apenas 3 MB [MT]",
    "基础截屏永久免费 · 录屏与 GIF 录制需 <a href=\"./#about\">SnipX Pro</a>（一次性买断）":
        "Captura básica grátis para sempre · gravação e GIF exigem <a href=\"./#about\">SnipX Pro</a> (compra única) [MT]",
    # about
    "关于 SnipX": "Sobre o SnipX [MT]",
    "原生开发": "Desenvolvimento nativo [MT]",
    "Swift + AppKit + SwiftUI + ScreenCaptureKit + AVFoundation + Carbon 编写，无 WebView、无 Electron、无包装层。":
        "Escrito em Swift + AppKit + SwiftUI + ScreenCaptureKit + AVFoundation + Carbon. Sem WebView, sem Electron, sem camada wrapper. [MT]",
    "隐私优先": "Privacidade em primeiro lugar [MT]",
    "内容处理在本机，无需注册 SnipX 账号。购买由 Apple 处理；主动分享由你选择。详见":
        "Todo o processamento acontece no seu Mac, sem conta SnipX. Compras passam pela Apple; compartilhar é sempre decisão sua. Detalhes em [MT]",
    "SnipX Pro": "SnipX Pro [MT]",
    "截屏、标注、长截图、置顶永久免费。一次性买断解锁 MP4 录屏与 GIF 录制，价格以 App Store 为准。":
        "Captura, anotação, captura de rolagem e fixar no topo são grátis para sempre. Uma compra única desbloqueia gravação MP4 e captura GIF. Preço definido na App Store. [MT]",
    "持续维护": "Manutenção contínua [MT]",
    "当前版本": "Versão atual [MT]",
    "每个版本均经过手测、单元测试、功能测试三道关。需要帮助？":
        "Cada versão passa por testes manuais, unitários e funcionais. Precisa de ajuda? [MT]",
    "支持页": "página de suporte [MT]",
    # footer
    "当前版本 1.0.0": "Versão atual 1.0.0 [MT]",
    # images alt
    "SnipX 界面预览": "Prévia da interface do SnipX [MT]",
    "SnipX 菜单栏截屏入口": "Atalho de captura do SnipX na barra de menus [MT]",
    "SnipX 全局快捷键设置": "Configurações de atalhos globais do SnipX [MT]",
    "SnipX 区域 / 窗口 / 全屏 / 长截图": "SnipX região / janela / tela cheia / captura de rolagem [MT]",
    "SnipX 本地 OCR 识别截图文字": "OCR local do SnipX reconhece texto das capturas [MT]",
    "SnipX 标注工具": "Ferramentas de anotação do SnipX [MT]",
    "SnipX MP4 录屏": "Gravação MP4 do SnipX [MT]",
    "SnipX 完全离线运行": "SnipX funciona totalmente offline [MT]",
    # privacy
    "Privacy Policy": "Privacy Policy",
    "SnipX 隐私政策": "Política de privacidade do SnipX [MT]",
    "最后更新：2026 年 9 月 6 日 · 适用于 SnipX macOS 应用与本站": "Última atualização: 6 de setembro de 2026 · aplica-se ao app SnipX para macOS e a este site [MT]",
    "内容在本机处理": "O conteúdo é processado no dispositivo [MT]",
    "截图、录屏、声音、摄像头画面、OCR 识别结果和标注均在你的 Mac 上处理。SnipX 不会自动把这些内容或本地诊断日志上传给开发者，不集成广告、追踪或第三方分析 SDK。":
        "Capturas, gravações, áudio, imagens da câmera, resultados de OCR e anotações são processados no seu Mac. O SnipX não envia seu conteúdo nem registros de diagnóstico locais, nem integra anúncios, rastreadores ou SDKs de terceiros. [MT]",
    "当你主动使用系统分享、发送反馈或将文件保存到云盘同步目录时，内容会按你的操作交给相应服务，其处理方式适用该服务的隐私政策。":
        "Ao usar o compartilhamento do sistema, enviar feedback ou salvar arquivos em uma pasta sincronizada na nuvem, o conteúdo é entregue ao serviço correspondente conforme sua ação, e a política de privacidade desse serviço se aplica. [MT]",
    "1. 系统权限": "1. Permissões do sistema [MT]",
    "屏幕录制：": "Gravação de tela: [MT]",
    "用于截屏、长截图与录屏。": "necessária para captura, captura de rolagem e gravação. [MT]",
    "系统声音：": "Áudio do sistema: [MT]",
    "在你启用电脑声音录制时写入本地视频。": "gravado no vídeo local ao ativar a captura de áudio do computador. [MT]",
    "麦克风：": "Microfone: [MT]",
    "在你开启麦克风录制时申请，用于录制声音。": "solicitado apenas ao ativar a captura de microfone, para gravar áudio. [MT]",
    "摄像头：": "Câmera: [MT]",
    "在你开启摄像头画面时申请，用于画中画。": "solicitado apenas ao ativar a sobreposição de câmera, para picture-in-picture. [MT]",
    "你可以在 macOS「系统设置 → 隐私与安全性」中管理权限。拒绝或撤销权限会影响对应功能。全局快捷键不要求额外开启辅助功能；在 Finder 中显示文件不要求自动化权限。":
        "Gerencie as permissões em Ajustes do Sistema → Privacidade e Segurança do macOS. Negar ou revogar uma permissão desativa o recurso relacionado. Atalhos globais não exigem Acessibilidade; mostrar arquivos no Finder não exige Automação. [MT]",
    "2. 文件、设置与本地日志": "2. Arquivos, ajustes e registros locais [MT]",
    "截图与录屏通过保存对话框导出到你选择的位置。录屏过程文件保存在应用支持目录的 SnipX/Recovery 中；本地诊断日志保存在 Library/Logs/SnipX/CrashLogs 中。沙盒版的这些应用目录位于 macOS 为 SnipX 分配的容器内，开发测试版也可能使用项目旁的 CrashLogs 目录。":
        "Capturas e gravações são exportadas por uma caixa de diálogo para o local que você escolher. Gravações em andamento ficam em SnipX/Recovery dentro do diretório de suporte do app; os registros diagnósticos vão para Library/Logs/SnipX/CrashLogs. Na versão em sandbox esses diretórios ficam dentro do contêiner que o macOS atribui ao SnipX; a versão de desenvolvimento pode usar uma pasta CrashLogs ao lado do projeto. [MT]",
    "应用在本机保存快捷键等偏好设置，并检查可用磁盘空间以保护录制文件。这些信息不会自动发送给开发者。OCR 使用 Apple Vision 框架在本机完成，不向服务器上传图片或识别结果。":
        "O app salva localmente preferências como atalhos e verifica o espaço em disco para proteger as gravações. Essas informações não são enviadas ao desenvolvedor automaticamente. O OCR roda localmente com o framework Apple Vision; imagens e resultados nunca vão para um servidor. [MT]",
    "删除应用本身不保证删除已导出文件、恢复文件和日志。请先保存需要保留的内容，再自行清理不需要的文件；不要在录制过程中删除恢复文件。":
        "Desinstalar o app não garante a exclusão de arquivos exportados, arquivos de recuperação ou registros. Salve antes o que quiser manter e depois remova o que não precisa. Não apague arquivos de recuperação durante uma gravação. [MT]",
    "3. 购买与恢复购买": "3. Compras e restauração [MT]",
    "SnipX Pro 为一次性买断的非消耗型内购，价格以 App 内和 Apple 购买确认界面为准。商品加载、购买、恢复及交易状态同步通过 Apple StoreKit 服务完成，可能需要联网。":
        "SnipX Pro é uma compra in-app não consumível de pagamento único. O preço é mostrado no app e na confirmação de compra da Apple. O carregamento do produto, a compra, a restauração e a sincronização do estado da transação passam pelo serviço StoreKit da Apple e podem exigir internet. [MT]",
    "Apple 处理付款。SnipX 在本机验证 Apple 提供的交易及权益信息，以决定是否解锁录屏和 GIF。开发者不通过应用收集你的银行卡或支付账户信息。Apple 对其处理的信息适用":
        "A Apple processa os pagamentos. O SnipX verifica localmente os dados de transação e entitlement fornecidos pela Apple para decidir se libera gravação e GIF. O desenvolvedor não coleta dados de cartão nem de conta de pagamento pelo app. Para as informações que a Apple trata, [MT]",
    "Apple 隐私政策": "vale a Política de Privacidade da Apple [MT]",
    "4. 主动联系支持与访问官网": "4. Contato com o suporte e visita ao site [MT]",
    "你主动发送邮件时，我们会收到你提供的邮箱、问题描述及附件，仅用于回复和排查问题。请勿发送无关的个人信息、密码或敏感截图；可以联系下方邮箱请求删除你提供的反馈材料。":
        "Quando você nos envia um e-mail, recebemos o endereço, a descrição do problema e os anexos fornecidos, usados apenas para responder e depurar. Não envie dados pessoais não relacionados, senhas nem capturas sensíveis. Você pode escrever para o endereço abaixo pedindo a exclusão do material enviado. [MT]",
    "本站没有加入广告或分析 SDK。网站托管服务可能处理提供页面和保障服务所需的 IP 地址、浏览器请求及访问日志；这与应用在本机处理截图的行为不同。":
        "Este site não inclui anúncios nem SDKs de análise. O provedor de hospedagem pode processar endereços IP, requisições do navegador e logs de acesso necessários para servir e proteger o site, algo diferente do processamento local de capturas no app. [MT]",
    "5. 政策变更与联系方式": "5. Alterações e contato [MT]",
    "隐私处理方式变化时，我们会更新本页面及更新日期。隐私问题或删除反馈材料的请求请联系":
        "Se nossas práticas de privacidade mudarem, atualizaremos esta página e sua data. Para dúvidas de privacidade ou pedidos de exclusão de material de feedback, escreva para [MT]",
    "使用说明见": "As instruções de uso estão em [MT]",
    "支持与帮助": "Suporte e ajuda [MT]",
    # support
    "Support": "Support",
    "SnipX 支持与帮助": "Suporte do SnipX [MT]",
    "FAQ、权限引导、反馈渠道 · 适用于 SnipX 1.0.0 及以上版本":
        "FAQ, guia de permissões e canais de feedback · para SnipX 1.0.0 e posteriores [MT]",
    "系统要求": "Requisitos do sistema [MT]",
    "macOS 14.0 Sonoma 或更高版本": "macOS 14.0 Sonoma ou superior [MT]",
    "支持 Apple Silicon（M1 / M2 / M3 / M4）与 Intel Mac": "Compatível com Apple Silicon (M1 / M2 / M3 / M4) e Mac Intel [MT]",
    "通用构建（Universal 2）同时包含": "A build Universal 2 inclui ambos [MT]",
    "截图、录屏与 OCR 在本机处理；商品加载、购买与恢复可能需要联网。":
        "Captura, gravação e OCR são processados no dispositivo; o carregamento do produto, compra e restauração podem exigir internet. [MT]",
    "首次启动：权限引导": "Primeira execução: guia de permissões [MT]",
    "SnipX 只会在你实际使用对应功能时申请系统权限，遵循 macOS 默认流程，不会启动即弹窗。":
        "O SnipX só pede permissões do sistema quando você realmente usa o recurso correspondente, seguindo o fluxo padrão do macOS, sem avisos ao iniciar. [MT]",
    "首次截屏或录屏时系统会弹窗。授权后到「系统设置 → 隐私与安全性 → 屏幕录制」可看到 SnipX。":
        "O macOS mostrará um aviso na sua primeira captura ou gravação. Depois de autorizar, você verá o SnipX em Ajustes do Sistema → Privacidade e Segurança → Gravação de Tela. [MT]",
    "仅在你开启「录制麦克风」开关时申请。": "Solicitado apenas ao ativar a captura de microfone. [MT]",
    "仅在你开启「录制摄像头」开关时申请。": "Solicitado apenas ao ativar a captura de câmera. [MT]",
    "录制电脑声音时，按 macOS 的屏幕与系统音频录制权限提示操作。":
        "Para capturar o áudio do computador, siga o aviso de permissão de tela e áudio do sistema do macOS. [MT]",
    "如果误点了「拒绝」，可以到「系统设置 → 隐私与安全性」手动开启；SnipX 内置的「权限」面板也会引导你跳转到对应位置。":
        "Se você tocou em \"Não permitir\" por engano, ative manualmente em Ajustes do Sistema → Privacidade e Segurança. O painel \"Permissões\" integrado do SnipX também leva você ao local certo. [MT]",
    "Q1：SnipX 联网吗？会上传我的截图吗？": "P1: O SnipX conecta à internet? Envia minhas capturas? [MT]",
    "截图、录屏、OCR 与标注在本机处理，不会自动上传给开发者。购买与恢复通过 Apple 服务完成，可能需要联网；主动分享或发邮件时，内容按你的操作交给相应服务。":
        "Captura, gravação, OCR e anotação são processados no dispositivo e nunca enviados ao desenvolvedor. Compras e restauração passam pela Apple e podem exigir internet. Se você compartilhar ou enviar por e-mail, o conteúdo é entregue ao serviço correspondente conforme sua ação. [MT]",
    "Q2：SnipX Pro 是什么？哪些功能需要付费？": "P2: O que é SnipX Pro? Quais recursos são pagos? [MT]",
    "截屏、标注、长截图、置顶、复制、保存、分享等基础功能永久免费。": "Captura, anotação, captura de rolagem, fixar, copiar, salvar, compartilhar e outros recursos básicos são grátis para sempre. [MT]",
    "（一次性买断，价格以 Apple 购买界面为准）": "(compra única, preço definido pela Apple) [MT]",
    "解锁：": "desbloqueia: [MT]",
    "MP4 录屏（选定区域 / 显示器）": "Gravação MP4 (região / monitor selecionado) [MT]",
    "GIF 录制": "Captura GIF [MT]",
    "系统声音 + 麦克风同时录制": "Áudio do sistema + microfone ao mesmo tempo [MT]",
    "摄像头画中画": "Câmera picture-in-picture [MT]",
    "倒计时与异常自动恢复": "Contagem regressiva e recuperação após falhas [MT]",
    "头尾裁剪导出": "Recortar início e fim e exportar [MT]",
    "Q3：如何恢复购买？": "P3: Como restauro uma compra? [MT]",
    "打开 SnipX → 菜单栏 → 设置 → 录屏 → 付费墙卡底部「恢复购买」按钮。App 会通过 StoreKit 2 重新校验你的购买状态。":
        "Abra o SnipX → barra de menus → Ajustes → Gravação → toque em \"Restaurar compra\" na parte inferior do cartão de pagamento. O app revalidará seu estado de compra via StoreKit 2. [MT]",
    "Q4：可以更换已授权的功能吗？": "P4: Posso alterar um recurso já autorizado? [MT]",
    "截屏、标注、长截图的快捷键都可以在「设置 → 快捷键」中自定义，冲突时会自动提示。":
        "Os atalhos de captura, anotação e captura de rolagem podem ser personalizados em Ajustes → Atalhos, com avisos automáticos em conflitos. [MT]",
    "Q5：为什么我截不到 SnipX 自己的窗口？": "P5: Por que não consigo capturar a própria janela do SnipX? [MT]",
    "SnipX 在录屏与截屏时会自动排除自身的菜单栏蒙层、操作浮层与录屏浮动条，避免污染画面。其他 SnipX 窗口（如设置、编辑录屏）默认会被正常捕获。":
        "Durante a captura ou gravação, o SnipX exclui automaticamente seus próprios overlays da barra de menus, popovers de ação e barra flutuante de gravação para manter a saída limpa. Outras janelas do SnipX (como Ajustes ou o editor de gravação) são capturadas normalmente. [MT]",
    "Q6：OCR 支持哪些语言？": "P6: Quais idiomas o OCR suporta? [MT]",
    "1.0.0 起，OCR 支持中文（简/繁）、英文及中英混合文本，由 Apple Vision 框架在本地完成识别，无网络依赖。":
        "A partir do 1.0.0, o OCR suporta chinês simplificado e tradicional, inglês e texto misto chinês/inglês, tudo reconhecido no dispositivo pelo framework Apple Vision, sem depender da rede. [MT]",
    "Q7：录屏文件保存在哪里？": "P7: Onde ficam minhas gravações? [MT]",
    "通过保存对话框导出到你选择的位置。录制过程文件保存在应用支持目录的 SnipX/Recovery 中，沙盒版位于 SnipX 的 macOS 容器内。应用会保留可恢复文件；退出前请先保存需要的内容。":
        "Exportadas por uma caixa de diálogo para o local que você escolher. Os arquivos em andamento ficam em SnipX/Recovery dentro do diretório de suporte do app (no contêiner do macOS para a versão sandbox). O app mantém arquivos recuperáveis; salve o que precisa antes de sair. [MT]",
    "反馈与问题上报": "Feedback e relato de bugs [MT]",
    "如果你遇到 bug、有功能建议或希望贡献想法：": "Encontrou um bug, tem uma ideia de recurso ou quer contribuir? [MT]",
    "邮箱：": "E-mail: [MT]",
    "请附上：macOS 版本、SnipX 版本、复现步骤、必要时附截图或录屏":
        "Inclua: versão do macOS, versão do SnipX, passos para reproduzir e, se possível, uma captura ou gravação [MT]",
    "SnipX 在异常退出时会保留崩溃日志到": "O SnipX preserva logs de falha em [MT]",
    "提交问题时一并附上可大幅加快定位": "anexá-los acelera muito a análise [MT]",
    "版本与更新": "Versões e atualizações [MT]",
    "当前最新版本：": "Versão mais recente: [MT]",
    "完整版本变更说明见": "As notas completas estão em [MT]",
    "相关链接": "Links relacionados [MT]",
    "产品主页": "Página do produto [MT]",
},
}


# ---------------------------------------------------------------------------
# HTML 模板：topbar / footer / head
# ---------------------------------------------------------------------------

HEAD_COMMON = '''<meta name="robots" content="index,follow" />
    <link id="favicon" rel="icon" href="/assets/brand/icon-snipx.png" />
    <script>
      /* 主题初始化（防 FOUC）：在 CSS 解析前完成 data-theme 设置 */
      (function () {{
        try {{
          var mode = localStorage.getItem("snipx-theme") || "system";
          var resolved = mode === "system"
            ? (window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark")
            : mode;
          document.documentElement.setAttribute("data-theme", resolved);
          document.documentElement.setAttribute("data-theme-mode", mode);
          var mc = document.querySelector('meta[name="theme-color"]');
          if (mc) mc.setAttribute("content", resolved === "light" ? "#f5f5f0" : "#050505");
        }} catch (e) {{}}
      }})();
    </script>
    <link rel="stylesheet" href="/assets/css/styles.css" />
    <link rel="stylesheet" href="/assets/css/i18n.css" />'''

TOPBAR_INNER = '''<a href="/{lang}/" class="topbar-brand" aria-label="SnipX">
            <img class="topbar-brand-mark" src="/assets/brand/icon-snipx.png" alt="" width="26" height="26" aria-hidden="true" />
            <span class="topbar-brand-text">SnipX</span>
          </a>

          <nav class="topbar-nav" aria-label="主导航">
            <a href="/{lang}/#features">__NAV_FEATURES__</a>
            <a href="/{lang}/#install">__NAV_DOWNLOAD__</a>
            <a href="/{lang}/#about">__NAV_ABOUT__</a>
          </nav>

          <div class="topbar-actions">
            <div class="lang-switcher">
              <button
                class="lang-switcher-toggle"
                type="button"
                aria-haspopup="listbox"
                aria-expanded="false"
                aria-label="__LANG_LABEL__"
              >
                <span class="lang-switcher-label">__LANG_SHORT__</span>
                <span class="lang-switcher-chevron" aria-hidden="true">⌄</span>
              </button>
              <ul class="lang-switcher-menu" role="listbox" hidden></ul>
            </div>
            <button
              class="theme-toggle"
              type="button"
              aria-label="__THEME_DEFAULT_LABEL__"
              title="__THEME_DEFAULT_LABEL__"
              data-mode="system"
            >
              <span class="theme-toggle-icon" aria-hidden="true">◐</span>
            </button>
            <a href="/{lang}/#install" class="topbar-cta">__TOPBAR_CTA__</a>
          </div>'''


FOOTER_INNER = '''<div class="footer-brand">
            <img class="topbar-brand-mark" src="/assets/brand/icon-snipx.png" alt="" width="26" height="26" aria-hidden="true" />
            <span class="footer-brand-text">SnipX</span>
          </div>

          <nav class="footer-links" aria-label="次要导航">
            <a href="/{lang}/">__NAV_HOME__</a>
            <a href="/{lang}/#features">__NAV_FEATURES__</a>
            <a href="/{lang}/#install">__NAV_DOWNLOAD__</a>
            <a href="/{lang}/support.html">__NAV_SUPPORT__</a>
            <a href="/{lang}/privacy.html">__NAV_PRIVACY__</a>
          </nav>

          <div class="footer-contact">
            <a href="mailto:snipx@tongkun.top" class="footer-contact-link">snipx@tongkun.top</a>
            <span class="footer-sep" aria-hidden="true">·</span>
            <span class="footer-meta">
              __FOOTER_VERSION_LABEL__ <span class="ph-version">1.0.0</span>
            </span>
          </div>

          <p class="footer-copyright">
            © 2026 SnipX. All rights reserved.
          </p>'''


SCRIPTS_TAIL = '''<script src="/assets/js/space-canvas.js" defer></script>
    <script src="/assets/js/site.js" defer></script>
    <script src="/assets/js/i18n.js" defer></script>'''


# Per-language meta config
META = {
    "zh-CN": {"html_lang": "zh-CN", "og_locale": "zh_CN"},
    "zh-TW": {"html_lang": "zh-TW", "og_locale": "zh_TW"},
    "en":    {"html_lang": "en", "og_locale": "en_US"},
    "ja":    {"html_lang": "ja", "og_locale": "ja_JP"},
    "ko":    {"html_lang": "ko", "og_locale": "ko_KR"},
    "es":    {"html_lang": "es", "og_locale": "es_ES"},
    "pt":    {"html_lang": "pt-BR", "og_locale": "pt_BR"},
}


# ---------------------------------------------------------------------------
# 翻译函数
# ---------------------------------------------------------------------------

def apply_translations(html: str, lang: str) -> str:
    """把中文原文替换为指定语言的译文。zh-CN 直接返回。

    去除 [MT] 标记（仅用于字典内部区分机译稿），并剥离 MT 标记后的
    尾随空格（如 `Descargar SnipX [MT]` → `Descargar SnipX`）。
    """
    if lang == "zh-CN":
        return html
    tr = T.get(lang, {})
    if not tr:
        sys.stderr.write(f"[warn] no translations for {lang}, falling back to zh-CN\n")
        return html
    # 长串优先，避免短串误命中
    items = sorted(tr.items(), key=lambda kv: -len(kv[0]))
    for src, tgt in items:
        # 字典内 [MT] 后缀仅作开发标记，从输出里去掉
        if src in html:
            clean_tgt = re.sub(r"\s*\[MT\]\s*$", "", tgt)
            html = html.replace(src, clean_tgt)
    return html


def fill_placeholders(template: str, lang: str) -> str:
    """把 __FOO__ 占位符按 lang 翻译后填回，并把 {lang} 替换为当前语种。"""
    template = template.replace("{lang}", lang)
    zh = T["zh-CN"]  # 不会真用
    # 我们需要每个占位符在当前语言里的值。
    # 因为占位符用的 token（如 __NAV_FEATURES__）不在 T 字典里，
    # 我们直接根据 lang 取占位符对应的中文，再翻译。
    # 占位符到中文的映射：
    tokens_zh = {
        "__NAV_FEATURES__": "特性",
        "__NAV_DOWNLOAD__": "下载",
        "__NAV_ABOUT__": "关于",
        "__NAV_HOME__": "主页",
        "__NAV_SUPPORT__": "支持",
        "__NAV_PRIVACY__": "隐私政策",
        "__TOPBAR_CTA__": "下载 SnipX",
        "__THEME_DEFAULT_LABEL__": "主题：跟随系统",
        "__FOOTER_VERSION_LABEL__": "当前版本",
    }
    tr = T.get(lang, {})
    for token, zh_str in tokens_zh.items():
        translated = tr.get(zh_str, zh_str)
        # 去除 [MT] 开发标记
        translated = re.sub(r"\s*\[MT\]\s*$", "", translated)
        template = template.replace(token, translated)
    # 切换器 placeholder
    lang_short = next((l["short"] for l in [
        {"code": "zh-CN", "short": "中文"},
        {"code": "zh-TW", "short": "繁體中文"},
        {"code": "en", "short": "English"},
        {"code": "ja", "short": "日本語"},
        {"code": "ko", "short": "한국어"},
        {"code": "es", "short": "Español"},
        {"code": "pt", "short": "Português"},
    ] if l["code"] == lang), "中文")
    template = template.replace("__LANG_SHORT__", lang_short)
    template = template.replace("__LANG_LABEL__", f"Language: {lang_short}")
    return template


# ---------------------------------------------------------------------------
# 页面生成
# ---------------------------------------------------------------------------

def page_html(lang: str, page: str, head_extra: str, body_html: str) -> str:
    """组装完整 HTML：head + topbar + body + footer + scripts。"""
    meta = META[lang]
    head = f'''<!doctype html>
<html lang="{meta["html_lang"]}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#050505" />
    {head_extra}
    {HEAD_COMMON}
'''
    topbar_html = f'''<header class="topbar{"" if page == "index" else " is-stuck"}" id="topbar">
        <div class="topbar-inner">
          {fill_placeholders(TOPBAR_INNER, lang)}
        </div>
      </header>'''
    footer_html = f'''<footer class="footer">
        <div class="footer-inner">
          {fill_placeholders(FOOTER_INNER, lang)}
        </div>
      </footer>'''
    scripts = SCRIPTS_TAIL

    full = f'''{head}
  <body>
    <canvas id="space-canvas" aria-hidden="true"></canvas>

    <div class="site-shell">
      {topbar_html}

      {body_html}

      {footer_html}
    </div>

    {scripts}
  </body>
</html>
'''
    # 应用翻译
    full = apply_translations(full, lang)
    return full


def body_index() -> str:
    return '''<main id="app">
        <!-- Hero -->
        <section id="home" class="hero">
          <div class="hero-meteors" aria-hidden="true"></div>
          <div class="hero-stardust" aria-hidden="true"></div>

          <div class="hero-inner">
            <div class="hero-copy">
              <p class="hero-eyebrow">macOS 14+ · 原生应用</p>
              <h1 class="hero-title">SnipX</h1>
              <p class="hero-title-note">
                Mac 截屏与录屏，一触即达。
              </p>
              <p class="hero-desc">
                原生 AppKit + Swift + ScreenCaptureKit。物理像素输出、本地 OCR、可编辑快捷键、长截图拼接、本地 MP4 录制。内容在本机处理，无需注册 SnipX 账号。
              </p>
              <p class="hero-tags">
                <span class="hero-tag">macOS 14+</span>
                <span class="hero-tag">Universal 2 · Apple Silicon + Intel</span>
                <span class="hero-tag">本地 OCR</span>
                <span class="hero-tag">SnipX Pro 录屏/GIF</span>
              </p>

              <div class="hero-cta">
                <a href="#install" class="btn btn-primary">下载 SnipX</a>
                <a href="#features" class="btn btn-ghost">查看功能</a>
              </div>
            </div>

            <div class="hero-visual">
              <div class="ph-image ph-image-hero" data-aspect="16/10">
                <img
                  src="/assets/screenshots/hero.jpg"
                  alt="SnipX 界面预览"
                  width="1920"
                  height="1152"
                  fetchpriority="high"
                />
              </div>
            </div>
          </div>
        </section>

        <!-- Features -->
        <section id="features" class="section features-section">
          <div class="section-head">
            <p class="section-eyebrow">特性</p>
            <h2 class="section-title">菜单栏常驻，所见即可截</h2>
            <p class="section-desc">
              截屏、标注、录屏、长截图，全部在菜单栏一触即达。
            </p>
          </div>

          <div class="features">
            <article class="feature-row" id="feature-menu">
              <div class="feature-visual">
                <div class="ph-image" data-aspect="16/10">
                  <img src="/assets/screenshots/feature-menu.webp" alt="SnipX 菜单栏截屏入口" width="1424" height="855" loading="lazy" />
                </div>
              </div>
              <div class="feature-copy">
                <p class="feature-eyebrow">常驻菜单栏</p>
                <h3 class="feature-title">点击即开，不打扰</h3>
                <p class="feature-desc">
                  SnipX 始终浮于屏幕角落的菜单栏。无需打开主窗口，点击即弹出截屏 / 录屏入口。
                </p>
                <ul class="feature-list">
                  <li>截屏、录屏、标注、设置 全部直达</li>
                  <li>不抢焦点、不打扰当前工作</li>
                  <li>原生菜单栏图标，遵循 macOS 设计语言</li>
                </ul>
              </div>
            </article>

            <article class="feature-row feature-row-reverse" id="feature-shortcut">
              <div class="feature-visual">
                <div class="ph-image" data-aspect="16/10">
                  <img src="/assets/screenshots/feature-shortcut.webp" alt="SnipX 全局快捷键设置" width="1362" height="912" loading="lazy" />
                </div>
              </div>
              <div class="feature-copy">
                <p class="feature-eyebrow">可编辑快捷键</p>
                <h3 class="feature-title">全局快捷键，自由绑定</h3>
                <p class="feature-desc">
                  截屏、录屏、标注、长截图 — 每个动作都可绑定独立快捷键，避免与其他应用冲突。
                </p>
                <ul class="feature-list">
                  <li>支持单键 / 组合键 / 修饰键</li>
                  <li>冲突检测，一键恢复默认</li>
                  <li>录屏、截屏独立绑定，标注即时唤起</li>
                </ul>
              </div>
            </article>

            <article class="feature-row" id="feature-modes">
              <div class="feature-visual">
                <div class="ph-image" data-aspect="16/10">
                  <img src="/assets/screenshots/feature-modes.webp" alt="SnipX 区域 / 窗口 / 全屏 / 长截图" width="1460" height="912" loading="lazy" />
                </div>
              </div>
              <div class="feature-copy">
                <p class="feature-eyebrow">四类截屏</p>
                <h3 class="feature-title">区域 / 窗口 / 全屏 / 长截图</h3>
                <p class="feature-desc">
                  物理像素输出，自动按显示器倍率渲染。窗口截屏自动识别应用窗口边缘，长截图无缝拼接。
                </p>
                <ul class="feature-list">
                  <li>区域截屏：拖拽选区，物理像素精度</li>
                  <li>窗口截屏：自动选窗，背景透明</li>
                  <li>全屏截屏：多显示器同时输出</li>
                  <li>长截图：滚动拼接，自动对齐</li>
                </ul>
              </div>
            </article>

            <article class="feature-row feature-row-reverse" id="feature-ocr">
              <div class="feature-visual">
                <div class="ph-image" data-aspect="16/10">
                  <img src="/assets/screenshots/feature-ocr.webp" alt="SnipX 本地 OCR 识别截图文字" width="1460" height="912" loading="lazy" />
                </div>
              </div>
              <div class="feature-copy">
                <p class="feature-eyebrow">本地 OCR（1.0.0 新增）</p>
                <h3 class="feature-title">截图里的文字，一键识别</h3>
                <p class="feature-desc">
                  基于 Apple Vision 框架，在你的 Mac 上直接识别截图中的中文、英文与中英混合文本。识别结果可编辑、可复制，不上传任何内容。
                </p>
                <ul class="feature-list">
                  <li>中文（简/繁）、英文与中英混排</li>
                  <li>完全本地识别，截图与文字不出本机</li>
                  <li>识别后可编辑、复制或取消</li>
                  <li>适用于截屏后的二次编辑与提取</li>
                </ul>
              </div>
            </article>

            <article class="feature-row" id="feature-annotation">
              <div class="feature-visual">
                <div class="ph-image" data-aspect="16/10">
                  <img src="/assets/screenshots/feature-annotation.webp" alt="SnipX 标注工具" width="1460" height="912" loading="lazy" />
                </div>
              </div>
              <div class="feature-copy">
                <p class="feature-eyebrow">标注工具</p>
                <h3 class="feature-title">矩形 / 箭头 / 文字 / 马赛克</h3>
                <p class="feature-desc">
                  截屏后即时标注，所有元素可移动、可删除、可撤销重做。裁剪、马赛克、颜色选择器一应俱全。
                </p>
                <ul class="feature-list">
                  <li>矩形、椭圆、箭头、画笔、文字</li>
                  <li>马赛克模糊敏感信息</li>
                  <li>撤销 / 重做 / 裁剪 / 颜色选择器</li>
                </ul>
              </div>
            </article>

            <article class="feature-row feature-row-reverse" id="feature-recording">
              <div class="feature-visual">
                <div class="ph-image" data-aspect="16/10">
                  <img src="/assets/screenshots/feature-recording.webp" alt="SnipX MP4 录屏" width="1460" height="912" loading="lazy" />
                </div>
              </div>
              <div class="feature-copy">
                <p class="feature-eyebrow">本地 MP4 录屏 · SnipX Pro</p>
                <h3 class="feature-title">倒计时 · 系统声 + 麦克风 · 自动恢复</h3>
                <p class="feature-desc">
                  基于 ScreenCaptureKit 本地录制，支持同时录制系统声音与麦克风，倒计时、磁盘保护、异常恢复一应俱全。头尾裁剪导出，无需第三方编辑器。
                </p>
                <ul class="feature-list">
                  <li>区域 / 窗口 / 显示器三种录屏模式</li>
                  <li>系统声音与麦克风同时录制，单一音轨</li>
                  <li>倒计时与状态指示，录屏不打断</li>
                  <li>异常退出后 Recovery 保留录制</li>
                  <li>头尾裁剪导出为新 MP4</li>
                </ul>
                <p class="feature-note">
                  录屏与 GIF 录制需解锁 <strong>SnipX Pro</strong>（一次性买断，价格以 App Store 为准）。截屏、标注、长截图永久免费。
                </p>
              </div>
            </article>

            <article class="feature-row" id="feature-privacy">
              <div class="feature-visual">
                <div class="ph-image" data-aspect="16/10">
                  <img src="/assets/screenshots/feature-privacy.webp" alt="SnipX 完全离线运行" width="1460" height="912" loading="lazy" />
                </div>
              </div>
              <div class="feature-copy">
                <p class="feature-eyebrow">零数据外传</p>
                <h3 class="feature-title">完全离线运行</h3>
                <p class="feature-desc">
                  截图、录屏与 OCR 在本机处理，不自动上传内容或遥测。购买与恢复通过 Apple 服务完成。
                </p>
                <ul class="feature-list">
                  <li>购买与恢复可能需要联网</li>
                  <li>无账号、无登录、无云同步</li>
                  <li>无第三方 SDK、无埋点</li>
                  <li>开源友好的本地存储</li>
                </ul>
              </div>
            </article>
          </div>
        </section>

        <!-- Install -->
        <section id="install" class="section install-section">
          <div class="section-head">
            <p class="section-eyebrow">下载</p>
            <h2 class="section-title">从 Mac App Store 获取</h2>
            <p class="section-desc">在 App Store 一键安装，内购、更新与恢复购买由 Apple 处理。</p>
          </div>

          <ol class="install-steps">
            <li class="install-step">
              <span class="install-step-num">1</span>
              <h3 class="install-step-title">前往 App Store</h3>
              <p class="install-step-desc">
                点击下方按钮，跳转 Mac App Store 的 SnipX 应用页。
              </p>
            </li>
            <li class="install-step">
              <span class="install-step-num">2</span>
              <h3 class="install-step-title">安装并打开</h3>
              <p class="install-step-desc">
                点按「获取」安装 SnipX，完成后从「应用程序」或菜单栏打开。
              </p>
            </li>
            <li class="install-step">
              <span class="install-step-num">3</span>
              <h3 class="install-step-title">授权系统权限</h3>
              <p class="install-step-desc">
                按所用功能授权：屏幕录制、系统声音、麦克风和摄像头。
              </p>
            </li>
          </ol>

          <div class="install-cta">
            <a
              id="appstore-download"
              href="#"
              data-appstore-url=""
              class="btn btn-primary btn-lg"
              aria-disabled="true"
            >前往 App Store 下载</a>
            <p class="install-pending">App Store 应用页即将上线，链接待回填。</p>
            <p class="install-req">macOS 14+ · Universal 2（Apple Silicon + Intel）· 仅 3 MB</p>
            <p class="install-pro">
              基础截屏永久免费 · 录屏与 GIF 录制需 <a href="./#about">SnipX Pro</a>（一次性买断）
            </p>
          </div>
        </section>

        <!-- About -->
        <section id="about" class="section about-section">
          <div class="section-head">
            <p class="section-eyebrow">关于</p>
            <h2 class="section-title">关于 SnipX</h2>
          </div>

          <div class="about-grid">
            <div class="about-card">
              <h3 class="about-card-title">原生开发</h3>
              <p class="about-card-desc">
                Swift + AppKit + SwiftUI + ScreenCaptureKit + AVFoundation + Carbon 编写，无 WebView、无 Electron、无包装层。
              </p>
            </div>
            <div class="about-card">
              <h3 class="about-card-title">隐私优先</h3>
              <p class="about-card-desc">
                内容处理在本机，无需注册 SnipX 账号。购买由 Apple 处理；主动分享由你选择。详见
                <a href="./privacy.html">隐私政策</a>。
              </p>
            </div>
            <div class="about-card">
              <h3 class="about-card-title">SnipX Pro</h3>
              <p class="about-card-desc">
                截屏、标注、长截图、置顶永久免费。一次性买断解锁 MP4 录屏与 GIF 录制，价格以 App Store 为准。
              </p>
            </div>
            <div class="about-card">
              <h3 class="about-card-title">持续维护</h3>
              <p class="about-card-desc">
                当前版本 <span class="ph-version">1.0.0</span>。每个版本均经过手测、单元测试、功能测试三道关。需要帮助？
                <a href="./support.html">支持页</a>。
              </p>
            </div>
          </div>
        </section>
      </main>'''


def body_privacy() -> str:
    return '''<main id="app" class="legal-page">
        <article class="legal">
          <header class="legal-head">
            <p class="legal-eyebrow">Privacy Policy</p>
            <h1 class="legal-title">SnipX 隐私政策</h1>
            <p class="legal-meta">最后更新：2026 年 9 月 6 日 · 适用于 SnipX macOS 应用与本站</p>
          </header>
          <section class="legal-section" id="privacy-summary">
            <header class="legal-section-head">
              <span class="legal-section-num">00</span>
              <h2>内容在本机处理</h2>
            </header>
            <p>截图、录屏、声音、摄像头画面、OCR 识别结果和标注均在你的 Mac 上处理。SnipX 不会自动把这些内容或本地诊断日志上传给开发者，不集成广告、追踪或第三方分析 SDK。</p>
            <p>当你主动使用系统分享、发送反馈或将文件保存到云盘同步目录时，内容会按你的操作交给相应服务，其处理方式适用该服务的隐私政策。</p>
          </section>
          <section class="legal-section" id="privacy-permissions">
            <header class="legal-section-head">
              <span class="legal-section-num">01</span>
              <h2>系统权限</h2>
            </header>
            <ul class="legal-list">
              <li><strong>屏幕录制：</strong>用于截屏、长截图与录屏。</li>
              <li><strong>系统声音：</strong>在你启用电脑声音录制时写入本地视频。</li>
              <li><strong>麦克风：</strong>在你开启麦克风录制时申请，用于录制声音。</li>
              <li><strong>摄像头：</strong>在你开启摄像头画面时申请，用于画中画。</li>
            </ul>
            <p>你可以在 macOS「系统设置 → 隐私与安全性」中管理权限。拒绝或撤销权限会影响对应功能。全局快捷键不要求额外开启辅助功能；在 Finder 中显示文件不要求自动化权限。</p>
          </section>
          <section class="legal-section" id="privacy-files">
            <header class="legal-section-head">
              <span class="legal-section-num">02</span>
              <h2>文件、设置与本地日志</h2>
            </header>
            <p>截图与录屏通过保存对话框导出到你选择的位置。录屏过程文件保存在应用支持目录的 SnipX/Recovery 中；本地诊断日志保存在 Library/Logs/SnipX/CrashLogs 中。沙盒版的这些应用目录位于 macOS 为 SnipX 分配的容器内，开发测试版也可能使用项目旁的 CrashLogs 目录。</p>
            <p>应用在本机保存快捷键等偏好设置，并检查可用磁盘空间以保护录制文件。这些信息不会自动发送给开发者。OCR 使用 Apple Vision 框架在本机完成，不向服务器上传图片或识别结果。</p>
            <p>删除应用本身不保证删除已导出文件、恢复文件和日志。请先保存需要保留的内容，再自行清理不需要的文件；不要在录制过程中删除恢复文件。</p>
          </section>
          <section class="legal-section" id="privacy-purchase">
            <header class="legal-section-head">
              <span class="legal-section-num">03</span>
              <h2>购买与恢复购买</h2>
            </header>
            <p>SnipX Pro 为一次性买断的非消耗型内购，价格以 App 内和 Apple 购买确认界面为准。商品加载、购买、恢复及交易状态同步通过 Apple StoreKit 服务完成，可能需要联网。</p>
            <p>Apple 处理付款。SnipX 在本机验证 Apple 提供的交易及权益信息，以决定是否解锁录屏和 GIF。开发者不通过应用收集你的银行卡或支付账户信息。Apple 对其处理的信息适用 <a href="https://www.apple.com/legal/privacy/" rel="noopener">Apple 隐私政策</a>。</p>
          </section>
          <section class="legal-section" id="privacy-contact">
            <header class="legal-section-head">
              <span class="legal-section-num">04</span>
              <h2>主动联系支持与访问官网</h2>
            </header>
            <p>你主动发送邮件时，我们会收到你提供的邮箱、问题描述及附件，仅用于回复和排查问题。请勿发送无关的个人信息、密码或敏感截图；可以联系下方邮箱请求删除你提供的反馈材料。</p>
            <p>本站没有加入广告或分析 SDK。网站托管服务可能处理提供页面和保障服务所需的 IP 地址、浏览器请求及访问日志；这与应用在本机处理截图的行为不同。</p>
          </section>
          <section class="legal-section" id="privacy-changes">
            <header class="legal-section-head">
              <span class="legal-section-num">05</span>
              <h2>政策变更与联系方式</h2>
            </header>
            <p>隐私处理方式变化时，我们会更新本页面及更新日期。隐私问题或删除反馈材料的请求请联系 <a href="mailto:snipx@tongkun.top">snipx@tongkun.top</a>。</p>
            <p>使用说明见 <a href="./support.html">支持与帮助</a>。</p>
          </section>
        </article>
      </main>'''


def body_support() -> str:
    return '''<main id="app" class="legal-page">
        <article class="legal">
          <header class="legal-head">
            <p class="legal-eyebrow">Support</p>
            <h1 class="legal-title">SnipX 支持与帮助</h1>
            <p class="legal-meta">
              FAQ、权限引导、反馈渠道 · 适用于 SnipX 1.0.0 及以上版本
            </p>
          </header>

          <section class="legal-section" id="support-requirements">
            <header class="legal-section-head">
              <span class="legal-section-num">00</span>
              <h2>系统要求</h2>
            </header>
            <ul class="sysreq">
              <li>macOS 14.0 Sonoma 或更高版本</li>
              <li>支持 Apple Silicon（M1 / M2 / M3 / M4）与 Intel Mac</li>
              <li>通用构建（Universal 2）同时包含 <code>arm64</code> 与 <code>x86_64</code></li>
              <li>截图、录屏与 OCR 在本机处理；商品加载、购买与恢复可能需要联网。</li>
            </ul>
          </section>

          <section class="legal-section" id="support-permissions">
            <header class="legal-section-head">
              <span class="legal-section-num">01</span>
              <h2>首次启动：权限引导</h2>
            </header>
            <p>
              SnipX 只会在你实际使用对应功能时申请系统权限，遵循 macOS
              默认流程，不会启动即弹窗。
            </p>
            <ol class="legal-list">
              <li>
                <strong>屏幕录制</strong>：首次截屏或录屏时系统会弹窗。授权后到「系统设置 → 隐私与安全性 →
                屏幕录制」可看到 SnipX。
              </li>
              <li>
                <strong>麦克风</strong>：仅在你开启「录制麦克风」开关时申请。
              </li>
              <li>
                <strong>摄像头</strong>：仅在你开启「录制摄像头」开关时申请。
              </li>
              <li><strong>系统声音：</strong>录制电脑声音时，按 macOS 的屏幕与系统音频录制权限提示操作。</li>
            </ol>
            <div class="legal-callout">
              <p>如果误点了「拒绝」，可以到「系统设置 → 隐私与安全性」手动开启；SnipX 内置的「权限」面板也会引导你跳转到对应位置。</p>
            </div>
          </section>

          <section class="legal-section" id="support-faq">
            <header class="legal-section-head">
              <span class="legal-section-num">02</span>
              <h2>FAQ</h2>
            </header>

            <div class="faq-item" id="faq-q1">
              <div class="faq-item-head">
                <span class="faq-item-q">Q1</span>
                <h3>Q1：SnipX 联网吗？会上传我的截图吗？</h3>
              </div>
              <div class="faq-item-body">
                <p>截图、录屏、OCR 与标注在本机处理，不会自动上传给开发者。购买与恢复通过 Apple 服务完成，可能需要联网；主动分享或发邮件时，内容按你的操作交给相应服务。</p>
              </div>
            </div>

            <div class="faq-item" id="faq-q2">
              <div class="faq-item-head">
                <span class="faq-item-q">Q2</span>
                <h3>Q2：SnipX Pro 是什么？哪些功能需要付费？</h3>
              </div>
              <div class="faq-item-body">
                <p>截屏、标注、长截图、置顶、复制、保存、分享等基础功能永久免费。<strong>SnipX Pro（一次性买断，价格以 Apple 购买界面为准）</strong>解锁：</p>
                <ul class="legal-list">
                  <li>MP4 录屏（选定区域 / 显示器）</li>
                  <li>GIF 录制</li>
                  <li>系统声音 + 麦克风同时录制</li>
                  <li>摄像头画中画</li>
                  <li>倒计时与异常自动恢复</li>
                  <li>头尾裁剪导出</li>
                </ul>
              </div>
            </div>

            <div class="faq-item" id="faq-q3">
              <div class="faq-item-head">
                <span class="faq-item-q">Q3</span>
                <h3>Q3：如何恢复购买？</h3>
              </div>
              <div class="faq-item-body">
                <p>打开 SnipX → 菜单栏 → 设置 → 录屏 → 付费墙卡底部「恢复购买」按钮。App 会通过 StoreKit 2 重新校验你的购买状态。</p>
              </div>
            </div>

            <div class="faq-item" id="faq-q4">
              <div class="faq-item-head">
                <span class="faq-item-q">Q4</span>
                <h3>Q4：可以更换已授权的功能吗？</h3>
              </div>
              <div class="faq-item-body">
                <p>截屏、标注、长截图的快捷键都可以在「设置 → 快捷键」中自定义，冲突时会自动提示。</p>
              </div>
            </div>

            <div class="faq-item" id="faq-q5">
              <div class="faq-item-head">
                <span class="faq-item-q">Q5</span>
                <h3>Q5：为什么我截不到 SnipX 自己的窗口？</h3>
              </div>
              <div class="faq-item-body">
                <p>SnipX 在录屏与截屏时会自动排除自身的菜单栏蒙层、操作浮层与录屏浮动条，避免污染画面。其他 SnipX 窗口（如设置、编辑录屏）默认会被正常捕获。</p>
              </div>
            </div>

            <div class="faq-item" id="faq-q6">
              <div class="faq-item-head">
                <span class="faq-item-q">Q6</span>
                <h3>Q6：OCR 支持哪些语言？</h3>
              </div>
              <div class="faq-item-body">
                <p>1.0.0 起，OCR 支持中文（简/繁）、英文及中英混合文本，由 Apple Vision 框架在本地完成识别，无网络依赖。</p>
              </div>
            </div>

            <div class="faq-item" id="faq-q7">
              <div class="faq-item-head">
                <span class="faq-item-q">Q7</span>
                <h3>Q7：录屏文件保存在哪里？</h3>
              </div>
              <div class="faq-item-body">
                <p>通过保存对话框导出到你选择的位置。录制过程文件保存在应用支持目录的 SnipX/Recovery 中，沙盒版位于 SnipX 的 macOS 容器内。应用会保留可恢复文件；退出前请先保存需要的内容。</p>
              </div>
            </div>
          </section>

          <section class="legal-section" id="support-feedback">
            <header class="legal-section-head">
              <span class="legal-section-num">03</span>
              <h2>反馈与问题上报</h2>
            </header>
            <p>如果你遇到 bug、有功能建议或希望贡献想法：</p>
            <ul class="legal-list">
              <li>邮箱：<a href="mailto:snipx@tongkun.top">snipx@tongkun.top</a></li>
              <li>请附上：macOS 版本、SnipX 版本、复现步骤、必要时附截图或录屏</li>
              <li>
                SnipX 在异常退出时会保留崩溃日志到
                <code>Library/Logs/SnipX/CrashLogs/（沙盒版位于应用容器内）</code
                >，提交问题时一并附上可大幅加快定位
              </li>
            </ul>
          </section>

          <section class="legal-section" id="support-versions">
            <header class="legal-section-head">
              <span class="legal-section-num">04</span>
              <h2>版本与更新</h2>
            </header>
            <p>
              当前最新版本：<strong>SnipX 1.0.0</strong>（OCR MVP + Universal 2）。
            </p>
            <p>
              完整版本变更说明见
              <a href="https://github.com/kenlez/SnipX/blob/main/RELEASE-NOTES.md" rel="noopener">RELEASE-NOTES.md</a>。
            </p>
          </section>

          <section class="legal-section" id="support-links">
            <header class="legal-section-head">
              <span class="legal-section-num">05</span>
              <h2>相关链接</h2>
            </header>
            <ul class="legal-list">
              <li><a href="./">产品主页</a></li>
              <li><a href="./privacy.html">隐私政策</a></li>
              <li>
                <a href="https://github.com/kenlez/SnipX" rel="noopener">SnipX GitHub</a>
              </li>
            </ul>
          </section>
        </article>
      </main>'''


def head_extra_index(lang: str) -> str:
    # index 页面有完整 meta description / og
    desc = {
        "zh-CN": 'SnipX 1.0.0：macOS 14+ 菜单栏截屏与 MP4 录屏原生应用。物理像素输出、本地 OCR、可编辑快捷键、长截图拼接、Universal 2（Apple Silicon + Intel）。内容在本机处理，无需注册 SnipX 账号。',
        "zh-TW": 'SnipX 1.0.0：macOS 14+ 選單列截圖與 MP4 錄螢原生應用程式。物理像素輸出、本地 OCR、可編輯快捷鍵、長截圖拼接、Universal 2（Apple Silicon + Intel）。內容在本機處理，無需註冊 SnipX 帳號。',
        "en": 'SnipX 1.0.0: a native macOS 14+ menu-bar app for screenshots and MP4 recording. Pixel-perfect output, on-device OCR, editable shortcuts, scrolling capture, Universal 2 (Apple Silicon + Intel). Everything stays on your Mac.',
        "ja": 'SnipX 1.0.0：macOS 14+ 対応、メニュー常駐のスクリーンショット・MP4 録画ネイティブアプリ。物理ピクセル出力、オンデバイス OCR、ショートカット編集可、スクロールキャプチャ、Universal 2（Apple Silicon + Intel）対応。すべて Mac 内で処理。',
        "ko": 'SnipX 1.0.0: macOS 14+ 메뉴바 스크린샷 및 MP4 녹화 네이티브 앱. 픽셀 정확 출력, 온디바이스 OCR, 단축키 편집, 스크롤 캡처, Universal 2 (Apple Silicon + Intel). 모든 처리는 Mac에서 로컬로.',
        "es": 'SnipX 1.0.0: aplicación nativa para macOS 14+ con captura de pantalla y grabación MP4 desde la barra de menús. Salida a píxel perfecto, OCR en el dispositivo, atajos editables, captura con desplazamiento, Universal 2 (Apple Silicon + Intel). Todo se procesa en tu Mac.',
        "pt": 'SnipX 1.0.0: app nativo macOS 14+ para captura de tela e gravação MP4 na barra de menus. Saída pixel-perfect, OCR no dispositivo, atalhos editáveis, captura com rolagem, Universal 2 (Apple Silicon + Intel). Tudo é processado no seu Mac.',
    }
    title = {
        "zh-CN": 'SnipX - Mac 截屏与录屏，一触即达',
        "zh-TW": 'SnipX - Mac 截圖與錄螢，一觸即達',
        "en": 'SnipX - Mac screenshots & recording, one tap away',
        "ja": 'SnipX - Mac のスクリーンショットと録画を、ワンタップで',
        "ko": 'SnipX - Mac 스크린샷 및 녹화, 원탭으로',
        "es": 'SnipX - Capturas y grabación en Mac, al instante',
        "pt": 'SnipX - Capturas e gravação no Mac, num toque',
    }
    meta = META[lang]
    return f'''<meta name="description" content="{desc[lang]}" />
    <meta property="og:title" content="{title[lang]}" />
    <meta property="og:description" content="{desc[lang]}" />
    <meta property="og:type" content="website" />
    <meta property="og:locale" content="{meta["og_locale"]}" />
    <meta property="og:image" content="/assets/brand/icon-snipx.png" />
    <title>{title[lang]}</title>'''


def head_extra_privacy(lang: str) -> str:
    desc = {
        "zh-CN": 'SnipX 隐私政策：截图、录屏与 OCR 在本机处理；购买通过 Apple 完成。',
        "zh-TW": 'SnipX 隱私政策：截圖、錄螢與 OCR 在本機處理；購買透過 Apple 完成。',
        "en": 'SnipX Privacy Policy: captures, recordings, and OCR are processed on-device; purchases go through Apple.',
        "ja": 'SnipX プライバシーポリシー：キャプチャ、録画、OCR はすべてデバイス上で処理されます。購入は Apple 経由です。',
        "ko": 'SnipX 개인정보 처리방침: 캡처, 녹화, OCR은 모두 기기에서 처리됩니다. 구매는 Apple을 통해 이루어집니다.',
        "es": 'Política de privacidad de SnipX: las capturas, grabaciones y OCR se procesan en el dispositivo; las compras pasan por Apple.',
        "pt": 'Política de privacidade do SnipX: capturas, gravações e OCR são processados no dispositivo; compras passam pela Apple.',
    }
    title = {
        "zh-CN": 'SnipX 隐私政策 · SnipX',
        "zh-TW": 'SnipX 隱私政策 · SnipX',
        "en": 'SnipX Privacy Policy · SnipX',
        "ja": 'SnipX プライバシーポリシー · SnipX',
        "ko": 'SnipX 개인정보 처리방침 · SnipX',
        "es": 'Política de privacidad de SnipX · SnipX',
        "pt": 'Política de privacidade do SnipX · SnipX',
    }
    meta = META[lang]
    return f'''<meta name="description" content="{desc[lang]}" />
    <meta property="og:title" content="{title[lang]}" />
    <meta property="og:description" content="{desc[lang]}" />
    <meta property="og:type" content="article" />
    <meta property="og:locale" content="{meta["og_locale"]}" />
    <title>{title[lang]}</title>'''


def head_extra_support(lang: str) -> str:
    desc = {
        "zh-CN": 'SnipX 支持页面：FAQ、权限引导、反馈渠道、系统要求与版本说明。',
        "zh-TW": 'SnipX 支援頁面：FAQ、權限引導、回饋渠道、系統需求與版本說明。',
        "en": 'SnipX Support: FAQ, permission guide, feedback channels, system requirements, and release notes.',
        "ja": 'SnipX サポート：FAQ、権限ガイド、フィードバックチャネル、システム要件、リリースノート。',
        "ko": 'SnipX 지원: FAQ, 권한 안내, 피드백 채널, 시스템 요구 사항 및 릴리스 노트.',
        "es": 'Soporte de SnipX: FAQ, guía de permisos, canales de feedback, requisitos del sistema y notas de versión.',
        "pt": 'Suporte do SnipX: FAQ, guia de permissões, canais de feedback, requisitos do sistema e notas de versão.',
    }
    title = {
        "zh-CN": 'SnipX 支持与帮助 · SnipX',
        "zh-TW": 'SnipX 支援與說明 · SnipX',
        "en": 'SnipX Support · SnipX',
        "ja": 'SnipX サポート · SnipX',
        "ko": 'SnipX 지원 · SnipX',
        "es": 'Soporte de SnipX · SnipX',
        "pt": 'Suporte do SnipX · SnipX',
    }
    meta = META[lang]
    return f'''<meta name="description" content="{desc[lang]}" />
    <meta property="og:title" content="{title[lang]}" />
    <meta property="og:description" content="{desc[lang]}" />
    <meta property="og:type" content="article" />
    <meta property="og:locale" content="{meta["og_locale"]}" />
    <title>{title[lang]}</title>'''


# ---------------------------------------------------------------------------
# 根目录自动跳转页（/、/privacy.html、/support.html）
# ---------------------------------------------------------------------------

ROOT_PICKER = '''<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#050505" />
    <meta name="robots" content="index,follow" />
    <meta
      name="description"
      content="SnipX — macOS 14+ native screenshot & MP4 recording app. Choose your language."
    />
    <title>SnipX</title>
    <script>
      /* 主题初始化（防 FOUC）：在 CSS 解析前完成 data-theme 设置 */
      (function () {{
        try {{
          var mode = localStorage.getItem("snipx-theme") || "system";
          var resolved = mode === "system"
            ? (window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark")
            : mode;
          document.documentElement.setAttribute("data-theme", resolved);
          document.documentElement.setAttribute("data-theme-mode", mode);
          var mc = document.querySelector('meta[name="theme-color"]');
          if (mc) mc.setAttribute("content", resolved === "light" ? "#f5f5f0" : "#050505");
        }} catch (e) {{}}
      }})();
      /* 语言自动跳转：匹配则跳子目录，否则显示手动选择器 */
      (function () {{
        try {{
          var stored = localStorage.getItem("snipx-lang");
          var raw = (stored || navigator.language || "en").toLowerCase();
          var codes = ["zh-cn","zh-tw","en","ja","ko","es","pt"];
          var match = codes.find(function (c) {{
            return raw === c || raw.startsWith(c.split("-")[0] + "-");
          }});
          if (match) {{
            var dir = match === "zh-cn" ? "zh-CN" :
                      match === "zh-tw" ? "zh-TW" : match;
            window.location.replace("/" + dir + "/{target}");
            return;
          }}
        }} catch (e) {{}}
        document.documentElement.classList.add("show-picker");
      }})();
    </script>
    <link rel="stylesheet" href="/assets/css/styles.css" />
    <link rel="stylesheet" href="/assets/css/i18n.css" />
    <link rel="stylesheet" href="/assets/css/picker.css" />
  </head>
  <body>
    <canvas id="space-canvas" aria-hidden="true"></canvas>

    <div class="site-shell">
      <header class="topbar is-stuck" id="topbar">
        <div class="topbar-inner">
          <a href="/" class="topbar-brand" aria-label="SnipX">
            <img class="topbar-brand-mark" src="/assets/brand/icon-snipx.png" alt="" width="26" height="26" aria-hidden="true" />
            <span class="topbar-brand-text">SnipX</span>
          </a>

          <nav class="topbar-nav" aria-label="主导航">
            <a href="/#features">特性</a>
            <a href="/#install">下载</a>
            <a href="/#about">关于</a>
          </nav>

          <div class="topbar-actions">
            <button
              class="theme-toggle"
              type="button"
              aria-label="主题：跟随系统"
              title="主题：跟随系统"
              data-mode="system"
            >
              <span class="theme-toggle-icon" aria-hidden="true">◐</span>
            </button>
          </div>
        </div>
      </header>

      <main id="app" class="picker-page">
        <section class="picker">
          <p class="picker-eyebrow">SnipX</p>
          <h1 class="picker-title">选择语言 · Choose your language</h1>
          <div class="picker-grid">
            <a href="/zh-CN/{target}" class="picker-card">
              <span class="picker-card-name">中文（简体）</span>
              <span class="picker-card-sub">Simplified Chinese</span>
            </a>
            <a href="/zh-TW/{target}" class="picker-card">
              <span class="picker-card-name">中文（繁體）</span>
              <span class="picker-card-sub">Traditional Chinese</span>
            </a>
            <a href="/en/{target}" class="picker-card">
              <span class="picker-card-name">English</span>
              <span class="picker-card-sub">English</span>
            </a>
            <a href="/ja/{target}" class="picker-card">
              <span class="picker-card-name">日本語</span>
              <span class="picker-card-sub">Japanese</span>
            </a>
            <a href="/ko/{target}" class="picker-card">
              <span class="picker-card-name">한국어</span>
              <span class="picker-card-sub">Korean</span>
            </a>
            <a href="/es/{target}" class="picker-card">
              <span class="picker-card-name">Español</span>
              <span class="picker-card-sub">Spanish</span>
            </a>
            <a href="/pt/{target}" class="picker-card">
              <span class="picker-card-name">Português</span>
              <span class="picker-card-sub">Portuguese</span>
            </a>
          </div>
        </section>
      </main>

      <footer class="footer">
        <div class="footer-inner">
          <div class="footer-brand">
            <img class="topbar-brand-mark" src="/assets/brand/icon-snipx.png" alt="" width="26" height="26" aria-hidden="true" />
            <span class="footer-brand-text">SnipX</span>
          </div>

          <nav class="footer-links" aria-label="次要导航">
            <a href="/">主页</a>
            <a href="/#features">特性</a>
            <a href="/#install">下载</a>
            <a href="/support.html">支持</a>
            <a href="/privacy.html">隐私政策</a>
          </nav>

          <div class="footer-contact">
            <a href="mailto:snipx@tongkun.top" class="footer-contact-link">snipx@tongkun.top</a>
            <span class="footer-sep" aria-hidden="true">·</span>
            <span class="footer-meta">当前版本 <span class="ph-version">1.0.0</span></span>
          </div>

          <p class="footer-copyright">© 2026 SnipX. All rights reserved.</p>
        </div>
      </footer>
    </div>

    <script src="/assets/js/space-canvas.js" defer></script>
    <script src="/assets/js/site.js" defer></script>
  </body>
</html>'''


def main():
    """主入口：生成 21 个语言页面 + 3 个根跳转页面。"""
    body_fns = {
        "index": (body_index, head_extra_index),
        "privacy": (body_privacy, head_extra_privacy),
        "support": (body_support, head_extra_support),
    }

    for lang in LANGS:
        out_dir = ROOT / lang
        out_dir.mkdir(exist_ok=True)
        for page in PAGES:
            body_fn, head_fn = body_fns[page]
            html = page_html(lang, page, head_fn(lang), body_fn())
            (out_dir / f"{page}.html").write_text(html, encoding="utf-8")
            print(f"  wrote {lang}/{page}.html ({len(html)} bytes)")

    # 根目录自动跳转页
    for page in PAGES:
        target = "" if page == "index" else f"{page}.html"
        html = ROOT_PICKER.format(target=target)
        (ROOT / f"{page if page != 'index' else 'index'}.html").write_text(html, encoding="utf-8")
        if page == "index":
            print(f"  wrote index.html (root auto-redirect)")
        else:
            print(f"  wrote {page}.html (root auto-redirect)")

    print("\nDone.")


if __name__ == "__main__":
    main()