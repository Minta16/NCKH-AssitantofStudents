import flet as ft
import requests
import json
import urllib3
import datetime
import os
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
TOKEN_FILE = "token.json"

COLOR_PRIMARY = "#0054a6" 
COLOR_SECONDARY = "#f39c12"
COLOR_BG_CHAT = "#f0f2f5"
COLOR_USER_BUBBLE = "#0084ff"
COLOR_BOT_BUBBLE = "#ffffff"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "apiKey": "pscRBF0zT2Mqo6vMw69YMOH43IrB2RtXBS0EHit2kzvL2auxaFJBvw==",
    "clientId": "vhu"
}

URLS = {
    "LOGIN": "https://portal_api.vhu.edu.vn/api/authenticate/authpsc",
    "LICH_HOC": "https://portal_api.vhu.edu.vn/api/student/DrawingSchedules",
    "HOC_PHI": "https://portal_api.vhu.edu.vn/api/student/AccountFeeHocPhan",
    "DIEM": "https://portal_api.vhu.edu.vn/api/student/marks",
    "LICH_THI": "https://portal_api.vhu.edu.vn/api/student/exam",
    "THONG_BAO": "https://portal_api.vhu.edu.vn/api/student/GetMessagesByReceiverID"
}

APP_STATE = {
    "token": "",
    "full_name": "",
    "mssv": "",  
    "nam_hoc": "",
    "hoc_ky": ""
}

# --- ĐÃ XÓA 2 DÒNG GÂY LỖI Ở ĐÂY ---

def khoitaoHK():
    today = datetime.datetime.now()
    month = today.month
    year = today.year
    if 9 <= month <= 12:
        APP_STATE["hoc_ky"] = "HK01"
        APP_STATE["nam_hoc"] = f"{year}-{year+1}"
    elif month == 1:
        APP_STATE["hoc_ky"] = "HK01"
        APP_STATE["nam_hoc"] = f"{year-1}-{year}"
    elif 2 <= month <= 5:
        APP_STATE["hoc_ky"] = "HK02"
        APP_STATE["nam_hoc"] = f"{year-1}-{year}"
    else:
        APP_STATE["hoc_ky"] = "HK03"
        APP_STATE["nam_hoc"] = f"{year-1}-{year}"

def save_token_to_file(data):
    try:
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Lỗi lưu file: {e}")

def load_token_from_file():
    if not os.path.exists(TOKEN_FILE): return None
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return None

def delete_token_file():
    if os.path.exists(TOKEN_FILE): os.remove(TOKEN_FILE)

def validate_token_alive(token):
    try:
        head = HEADERS.copy()
        head["Authorization"] = f"Bearer {token}"
        resp = requests.get(URLS["HOC_PHI"], headers=head, verify=False, timeout=5)
        return resp.status_code == 200
    except: return False

def main(page: ft.Page):
    page.title = "Trường Đại học Văn Hiến - Trợ lý ảo"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400
    page.window_height = 800
    page.padding = 0
    page.spacing = 0
    page.bgcolor = COLOR_BG_CHAT
    page.fonts = {"Roboto": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf"}
    page.theme = ft.Theme(font_family="Roboto", color_scheme_seed=COLOR_PRIMARY)
    
    khoitaoHK()

    def show_chat_screen():
        page.clean()
        
        # --- XỬ LÝ TÊN RIÊNG AN TOÀN ---
        full_name = APP_STATE.get('full_name', '').strip()
        if full_name:
            ten_rieng = full_name.split()[-1]
        else:
            ten_rieng = "Bạn"
        # -------------------------------

        chat_list = ft.ListView(
            expand=True, 
            spacing=15, 
            padding=ft.padding.all(15), 
            auto_scroll=True
        )

        txt_input = ft.TextField(
            hint_text="Nhập yêu cầu...",
            border_radius=25,
            filled=True,
            bgcolor=ft.Colors.WHITE,
            border_color=ft.Colors.TRANSPARENT,
            content_padding=ft.padding.only(left=20, right=10, top=10, bottom=10),
            expand=True,
            text_size=15
        )

        def logout_click(e):
            delete_token_file()
            APP_STATE['token'] = ""
            show_login_screen()

        def add_message(text, is_user=False):
            avatar = ft.CircleAvatar(
                content=ft.Icon(ft.Icons.PERSON if is_user else ft.Icons.SMART_TOY, size=20, color=ft.Colors.WHITE),
                bgcolor=COLOR_PRIMARY if not is_user else ft.Colors.GREY_500,
                radius=18
            )
            
            bubble_color = COLOR_USER_BUBBLE if is_user else COLOR_BOT_BUBBLE
            text_color = ft.Colors.WHITE if is_user else ft.Colors.BLACK87
            
            if is_user:
                border_radius = ft.border_radius.only(top_left=15, top_right=15, bottom_left=15, bottom_right=0)
            else:
                border_radius = ft.border_radius.only(top_left=15, top_right=15, bottom_left=0, bottom_right=15)

            msg_content = ft.Markdown(
                text, 
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                on_tap_link=lambda e: page.launch_url(e.data)
            ) if not is_user else ft.Text(text, color=text_color, size=15)

            bubble = ft.Container(
                content=msg_content,
                padding=ft.padding.symmetric(vertical=10, horizontal=15),
                border_radius=border_radius,
                bgcolor=bubble_color,
                shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.BLACK12, offset=ft.Offset(0, 1)),
                width=300 if len(text) > 30 else None, 
            )

            row_controls = [bubble, ft.Container(width=5), avatar] if is_user else [avatar, ft.Container(width=5), bubble]
            alignment = ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
            
            chat_list.controls.append(
                ft.Row(
                    controls=row_controls,
                    alignment=alignment,
                    vertical_alignment=ft.CrossAxisAlignment.END
                )
            )
            page.update()

        def process_bot_reply(msg):
            # --- CHUẨN BỊ DỮ LIỆU ---
            fn = APP_STATE.get('full_name', '').strip()
            ten = fn.split()[-1] if fn else "Bạn"
            
            m = msg.lower() # Chuyển tin nhắn về chữ thường
            head = HEADERS.copy()
            head["Authorization"] = f"Bearer {APP_STATE['token']}"

            # --- 1. CHÀO HỎI ---
            if any(k in m for k in [ "chào", "hello", "halo", "chao"]):
                add_message(f"👋 Chào {ten}! Mình là trợ lý ảo VHU.\nBạn có thể hỏi: **Lịch học**, **Lịch thi**, **Học phí**, hoặc **Thông báo**.", False)
                return
            
            # --- 2. THÔNG TIN CÁ NHÂN ---
            if any(k in m for k in ["thông tin", "info", "profile", "mssv"]):
                add_message(f"**HỒ SƠ SINH VIÊN:**\n\n👤 Tên: **{APP_STATE['full_name']}**\n\n 🎓 MSSV: {APP_STATE['mssv']}\n\n📅 Năm học: {APP_STATE['nam_hoc']} ({APP_STATE['hoc_ky']})", False)
                return
            
            # --- 3. LỊCH HỌC ---
            if any(k in m for k in ["lịch học", "tkb", "thời khóa biểu", "lich hoc", "tuan sau"]):  
                is_next = "tuần sau" in m or "tuan sau" in m
                week_now = datetime.datetime.now().isocalendar()[1]
                week_check = week_now + 1 if is_next else week_now
                
                add_message(f"⏳ Đang tải lịch học tuần {week_check}...", False)
                try:
                    resp = requests.get(URLS["LICH_HOC"], headers=head, params={"namhoc": APP_STATE["nam_hoc"], "hocky": APP_STATE["hoc_ky"], "tuan": week_check}, verify=False, timeout=10)
                    data = resp.json().get("ResultDataSchedule", [])
                    
                    if not data: 
                        add_message(f"📭 Tuần {week_check} không có lịch học.", False)
                    else:
                        reply = f"**📅 LỊCH TUẦN {week_check}:**\n"
                        for i in data: 
                            ngay = i.get('DayName', '')
                            ngay_so = i.get('Date', '')[:5]
                            mon = i.get('CurriculumName', 'Môn học')
                            phong = str(i.get('RoomID', 'Unknown')).replace('</br>','-')
                            tiet = str(i.get('CaHoc', ''))
                            reply += f"🔹 **{ngay}** ({ngay_so}) - Tiết {tiet}\n   📖 {mon}\n   📍 P.{phong}\n\n"
                        add_message(reply, False)
                except Exception as e: 
                    add_message(f"❌ Lỗi tải lịch học: {e}", False)
                return

            # --- 4. THÔNG BÁO ---
            if any(k in m for k in ["thông báo", "tin nhắn", "news"]):
                add_message("🔔 Đang tải 5 thông báo mới nhất...\n", False)
                try:
                    resp = requests.get(URLS["THONG_BAO"], headers=head, params={"pageIndex": 1, "pageSize": 5}, verify=False, timeout=10)
                    if resp.status_code == 200:
                        raw = resp.json()
                        data = raw if isinstance(raw, list) else raw.get("ListItems", [])
                        if not data: add_message("📭 Không có thông báo mới.", False)
                        else:
                            reply = "**🔔 5 TIN MỚI NHẤT:**\n"
                            for item in data[:5]:
                                date = item.get("CreationDate", "--/--")
                                sub = item.get("MessageSubject", "Không tiêu đề")
                                reply += f"🔸 *{date}*:\n**{sub}**\n\n"
                            add_message(reply, False)
                    else: add_message("⚠️ Lỗi Server.", False)
                except Exception as e: add_message(f"❌ Lỗi kết nối: {e}", False)
                return

            # --- 5. HỌC PHÍ ---
            kw_hocphi = ["học phí", "tiền học", "tien hoc", "công nợ", "nợ"]
            if any(k in m for k in kw_hocphi):
                add_message("💰 Đang kiểm tra sổ nợ...", False)
                try:
                    resp = requests.get(URLS["HOC_PHI"], headers=head, verify=False, timeout=10)
                    data = resp.json()
                    raw_list = data if isinstance(data, list) else data.get("DanhSachKhoanThu", [])
                    ds_no = [x for x in raw_list if x.get("ConNo", 0) > 0]
                    tong = sum(x.get("ConNo", 0) for x in ds_no)
                    
                    if tong == 0: add_message(f"🎉 Tuyệt vời! {ten} không nợ đồng nào.", False)
                    else:
                        reply = f"💸 **TỔNG NỢ: {tong:,.0f} VNĐ*\n"
                        for x in ds_no: reply += f"\n🔻 {x['FeeName']}\n   👉 {x['ConNo']:,.0f}đ\n"
                        add_message(reply, False)
                        add_message(f"⚠️ {ten} nhớ đóng học phí sớm nhé!", False)
                except Exception as e: add_message(f"❌ Lỗi: {e}", False)
                return

            # --- 6. LỊCH THI (ĐÃ SỬA LỖI) ---
            # Bắt từ khóa: Lịch thi, ngày thi, bao giờ thi...
            if any(k in m for k in ["lịch thi", "lich thi", "ngày thi", "ngay thi", "khi nào thi", "bao gio thi"]):
                add_message(f"✍️ Đang tải lịch thi {APP_STATE['hoc_ky']}...", False)
                try:
                    # In ra console để kiểm tra xem năm học có đúng không
                    print(f"DEBUG: Đang lấy lịch thi năm {APP_STATE['nam_hoc']} - {APP_STATE['hoc_ky']}")
                    
                    params = {"namhoc": APP_STATE["nam_hoc"], "hocky": APP_STATE["hoc_ky"]}
                    resp = requests.get(URLS["LICH_THI"], headers=head, params=params, verify=False, timeout=10)
                    
                    # Nếu Token hết hạn hoặc Server lỗi
                    if resp.status_code != 200:
                        add_message(f"⚠️ Không lấy được dữ liệu (Lỗi {resp.status_code})", False)
                        return

                    data = resp.json()
                    
                    if not data: 
                        add_message(f"📭 Hiện chưa có lịch thi nào cho {APP_STATE['hoc_ky']}.", False)
                    else:
                        # Sắp xếp ngày thi (dùng try-except để không bị crash nếu ngày null)
                        try:
                            data.sort(key=lambda x: datetime.datetime.strptime(x.get('NgayThi', '01/01/2000'), "%d/%m/%Y"))
                        except: pass 

                        reply = f"**🏆 LỊCH THI {APP_STATE['hoc_ky']}:**\n"
                        for x in data:
                            # Lấy dữ liệu an toàn, nếu thiếu thì điền mặc định
                            ngay = x.get('NgayThi')
                            gio = x.get('GioThi')
                            
                            # Nếu chưa có ngày giờ thi cụ thể
                            if not ngay or not gio:
                                time_str = "⏳ Chưa có lịch cụ thể"
                            else:
                                time_str = f"📅 **{ngay}** lúc **{gio}**"

                            mon = x.get('CurriculumName', 'Môn học')
                            phong = x.get('PhongThi', 'Chưa báo phòng')
                            hinh_thuc = x.get('HinhThucThi', '')
                            
                            reply += f"{time_str}\n📖 {mon}\n📍 P.{phong} ({hinh_thuc})\n\n"
                        add_message(reply, False)
                except Exception as e: 
                    # In lỗi chi tiết ra để sửa
                    print(f"LỖI LỊCH THI: {e}")
                    add_message(f"❌ Có lỗi khi tải lịch thi. Bạn hãy thử lại sau nhé.", False)
                return

            # --- 7. MẶC ĐỊNH ---
            add_message(f"Xin lỗi {ten}, mình chưa hiểu câu này. 😅\nThử gõ: 'Lịch học', 'Học phí', 'Lịch thi' xem sao!", False)

        def send_click(e):
            if not txt_input.value: return
            t = txt_input.value
            txt_input.value = ""
            add_message(t, True)
            process_bot_reply(t)
            txt_input.focus()
            
        txt_input.on_submit = send_click

        bottom_bar = ft.Container(
            content=ft.Column([
                ft.Row([
                    txt_input,
                    ft.IconButton(
                        icon=ft.Icons.SEND_ROUNDED, 
                        icon_color=COLOR_PRIMARY, 
                        icon_size=30,
                        on_click=send_click,
                        tooltip="Gửi"
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ]),
            padding=ft.padding.all(10),
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12, offset=ft.Offset(0, -2))
        )

        page.appbar = ft.AppBar(
            leading=ft.Icon(ft.Icons.SCHOOL, color=ft.Colors.WHITE),
            title=ft.Text(f"Hi, {ten_rieng}", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD), # Đã dùng biến an toàn
            actions=[ft.IconButton(ft.Icons.LOGOUT, icon_color=ft.Colors.WHITE, on_click=logout_click, tooltip="Đăng xuất")],
            bgcolor=COLOR_PRIMARY,
            elevation=2
        )

        page.add(ft.Column([chat_list, bottom_bar], expand=True, spacing=0))
        add_message(f"👋 Chào **{APP_STATE['full_name']}**! Mình là trợ lý ảo VHU.\nBạn cần tra cứu gì hôm nay?", False)

    def show_login_screen():
        page.clean()
        
        txt_u = ft.TextField(
            label="Mã số sinh viên", 
            prefix_icon=ft.Icons.PERSON_OUTLINE, 
            border_radius=15, 
            filled=True, 
            bgcolor=ft.Colors.WHITE
        )
        txt_p = ft.TextField(
            label="Mật khẩu", 
            password=True, 
            can_reveal_password=True, 
            prefix_icon=ft.Icons.LOCK_OUTLINE, 
            border_radius=15, 
            filled=True, 
            bgcolor=ft.Colors.WHITE
        )
        err = ft.Text("", color="red", size=14, italic=True)
        btn_login = ft.ElevatedButton(
            text="ĐĂNG NHẬP",
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=COLOR_PRIMARY,
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=20
            ),
            width=300,
            on_click=lambda e: login(e)
        )
        
        loading = ft.ProgressBar(width=200, color=COLOR_SECONDARY, visible=False)

        def login(e):
            err.value = ""
            loading.visible = True
            btn_login.disabled = True
            page.update()
            
            try:
                time.sleep(0.5)
                resp = requests.post(URLS["LOGIN"], headers=HEADERS, data=json.dumps({"username": txt_u.value, "password": txt_p.value, "type": 0}), verify=False)
                if resp.status_code == 200 and "Token" in resp.json():
                    d = resp.json()
                    
                    mssv_hien_tai = txt_u.value
                    
                    APP_STATE.update({
                        "token": d['Token'], 
                        "full_name": d['FullName'], 
                        "mssv": mssv_hien_tai
                    })
                    
                    save_token_to_file({
                        "token": d['Token'], 
                        "full_name": d['FullName'], 
                        "mssv": mssv_hien_tai
                    })
                    
                    show_chat_screen()
                else: 
                    err.value = "Sai tài khoản hoặc mật khẩu!"
            except Exception as ex:
                err.value = f"Lỗi kết nối: {ex}"
            
            loading.visible = False
            btn_login.disabled = False
            page.update()

        card = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=80, color=COLOR_PRIMARY),
                    ft.Text("Trường Đại học Văn Hiến", size=24, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                    ft.Text("Cổng thông tin sinh viên", size=14, color=ft.Colors.GREY),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    txt_u,
                    txt_p,
                    err,
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    loading,
                    btn_login
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=30,
            bgcolor=ft.Colors.WHITE,
            border_radius=20,
            shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.BLACK12, offset=ft.Offset(0, 5)),
            width=350
        )

        page.add(
            ft.Container(
                content=card,
                expand=True,
                alignment=ft.alignment.center,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=[COLOR_PRIMARY, "#6dd5fa"]
                )
            )
        )

    saved = load_token_from_file()
    if saved and validate_token_alive(saved.get("token")):
        APP_STATE.update(saved)
        show_chat_screen()
    else:
        show_login_screen()

ft.app(target=main)