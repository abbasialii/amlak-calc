import flet as ft

# ================= تابع تبدیل عدد به حروف فارسی =================
def num_to_persian_words(n):
    if n == 0: return "صفر"
    
    ones = ["", "یک", "دو", "سه", "چهار", "پنج", "شش", "هفت", "هشت", "نه"]
    tens = ["", "ده", "بیست", "سی", "چهارل", "پنجاه", "شصت", "هفتاد", "هشتاد", "نود"]
    teens = ["ده", "یازده", "دوازده", "سیزده", "چهارده", "پانزده", "شانزده", "هفده", "هجده", "نوزده"]
    hundreds = ["", "صد", "دویست", "سیصد", "چهارصد", "پانصد", "ششصد", "هفتصد", "هشتصد", "نهصد"]
    magnitudes = ["", " هزار", " میلیون", " میلیارد", " هزار میلیارد"]
    
    def convert_less_than_1000(num):
        if num == 0: return ""
        res = []
        h = num // 100
        if h > 0: res.append(hundreds[h])
        rem = num % 100
        if 10 <= rem <= 19:
            res.append(teens[rem - 10])
        else:
            t = rem // 10
            if t > 0: res.append(tens[t].replace("چهارل", "چهل"))
            o = rem % 10
            if o > 0: res.append(ones[o])
        return " و ".join(res)
        
    parts = []
    mag_index = 0
    while n > 0:
        chunk = n % 1000
        if chunk > 0:
            chunk_str = convert_less_than_1000(chunk)
            parts.append(chunk_str + magnitudes[mag_index])
        n //= 1000
        mag_index += 1
        
    return " و ".join(reversed(parts))

def main(page: ft.Page):
    # ================= تنظیمات اصلی =================
    page.title = "محاسبه کمیسیون"
    page.window.width = 420
    page.window.height = 800
    page.theme_mode = ft.ThemeMode.LIGHT
    page.rtl = True
    page.padding = 0
    page.bgcolor = "#F2F4F7"
    page.scroll = ft.ScrollMode.AUTO

    BLUE_COLOR = "#1D5BBA"
    
    def format_input(e):
        raw_value = e.control.value.replace(",", "")
        if raw_value.isdigit():
            e.control.value = f"{int(raw_value):,}"
        else:
            e.control.value = ""
        e.control.update()

    def get_raw_value(formatted_str):
        if not formatted_str: return 0
        return int(formatted_str.replace(",", ""))

    # هدر آبی
    header = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.icons.HOME, color=ft.colors.WHITE, size=24),
                ft.Text("دستیار هوشمند املاک", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Text("محاسبه‌گر دقیق کمیسیون و مالیات", size=12, color=ft.colors.WHITE70)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=BLUE_COLOR,
        height=120,
        border_radius=ft.border_radius.only(bottom_left=35, bottom_right=35),
        padding=ft.padding.only(top=30),
        shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.BLACK12, offset=ft.Offset(0, 5))
    )

    def create_modern_input(label, icon, on_change_func):
        tf = ft.TextField(
            label=label,
            prefix_icon=icon,
            border=ft.InputBorder.NONE,
            bgcolor=ft.colors.TRANSPARENT,
            text_align=ft.TextAlign.LEFT,
            on_change=on_change_func,
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9,]"),
            content_padding=15
        )
        container = ft.Container(
            content=tf,
            bgcolor=ft.colors.WHITE,
            border_radius=20,
            shadow=ft.BoxShadow(blur_radius=15, color=ft.colors.BLACK12, offset=ft.Offset(0, 5))
        )
        return tf, container

    # ================= بخش خرید و فروش =================
    sale_word_txt = ft.Text(value="", size=12, color=BLUE_COLOR, weight=ft.FontWeight.W_500)

    def on_sale_change(e):
        format_input(e)
        val = get_raw_value(e.control.value)
        sale_word_txt.value = f"{num_to_persian_words(val)} تومان" if val > 0 else ""
        page.update()

    sale_input, sale_input_container = create_modern_input("مبلغ کل معامله (تومان)", ft.icons.ACCOUNT_BALANCE_WALLET, on_sale_change)

    s_total_income = ft.Text("۰", size=32, weight=ft.FontWeight.BOLD, color=BLUE_COLOR)
    s_party_share = ft.Text("۰", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.GREY_800)
    s_base_txt = ft.Text("-", size=13, color=ft.colors.GREY_600)
    s_tax_txt = ft.Text("-", size=13, color=ft.colors.GREY_600)

    sale_result_card = ft.Container(
        content=ft.Column([
            ft.Text("مجموع درآمد دفتر", size=13, color=ft.colors.GREY_500),
            s_total_income,
            ft.Divider(color=ft.colors.GREY_200, height=20),
            ft.Text("سهم قابل پرداخت هر طرف", size=13, color=ft.colors.GREY_500),
            s_party_share,
            ft.Container(height=5),
            ft.Row([ft.Icon(ft.icons.CHECK_CIRCLE, size=14, color=ft.colors.GREEN), s_base_txt]),
            ft.Row([ft.Icon(ft.icons.MONETIZATION_ON, size=14, color=ft.colors.RED_400), s_tax_txt]),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
        bgcolor=ft.colors.WHITE,
        border_radius=25,
        padding=25,
        shadow=ft.BoxShadow(blur_radius=20, color=ft.colors.BLACK12, offset=ft.Offset(0, 10)),
        visible=False
    )

    def calc_sale(e):
        total = get_raw_value(sale_input.value)
        if total == 0: return
        base = total * 0.005 if total <= 50_000_000 else (50_000_000 * 0.005) + ((total - 50_000_000) * 0.0025)
        tax = base * 0.09
        final_party = base + tax
        
        s_total_income.value = f"{final_party * 2:,.0f} ₸"
        s_party_share.value = f"{final_party:,.0f} تومان"
        s_base_txt.value = f"کمیسیون خالص: {base:,.0f} تومان"
        s_tax_txt.value = f"مالیات (۹٪): {tax:,.0f} تومان"
        
        sale_result_card.visible = True
        page.update()

    sale_view = ft.Column([
        ft.Container(height=5),
        sale_input_container,
        ft.Container(content=sale_word_txt, padding=ft.padding.only(right=10)),
        ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.icons.CALCULATE), ft.Text("مـحـاسـبـه", size=16, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=BLUE_COLOR, color=ft.colors.WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20), padding=20),
            on_click=calc_sale
        ),
        ft.Container(height=5),
        sale_result_card
    ])

    # ================= بخش رهن و اجاره =================
    mortgage_word_txt = ft.Text(value="", size=12, color=BLUE_COLOR, weight=ft.FontWeight.W_500)
    rent_word_txt = ft.Text(value="", size=12, color=BLUE_COLOR, weight=ft.FontWeight.W_500)

    def on_mortgage_change(e):
        format_input(e)
        val = get_raw_value(e.control.value)
        mortgage_word_txt.value = f"{num_to_persian_words(val)} تومان" if val > 0 else ""
        page.update()

    def on_rent_change(e):
        format_input(e)
        val = get_raw_value(e.control.value)
        rent_word_txt.value = f"{num_to_persian_words(val)} تومان" if val > 0 else ""
        page.update()

    mortgage_input, mortgage_container = create_modern_input("مبلغ رهن / پول پیش (تومان)", ft.icons.KEY, on_mortgage_change)
    rent_input, rent_container = create_modern_input("مبلغ اجاره ماهیانه (تومان)", ft.icons.MONETIZATION_ON, on_rent_change)

    r_total_income = ft.Text("۰", size=32, weight=ft.FontWeight.BOLD, color=BLUE_COLOR)
    r_party_share = ft.Text("۰", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.GREY_800)
    r_eq_txt = ft.Text("-", size=13, color=ft.colors.GREY_600)
    r_base_txt = ft.Text("-", size=13, color=ft.colors.GREY_600)
    r_tax_txt = ft.Text("-", size=13, color=ft.colors.GREY_600)

    rent_result_card = ft.Container(
        content=ft.Column([
            ft.Text("مجموع درآمد دفتر", size=13, color=ft.colors.GREY_500),
            r_total_income,
            ft.Divider(color=ft.colors.GREY_200, height=20),
            ft.Text("سهم قابل پرداخت هر طرف", size=13, color=ft.colors.GREY_500),
            r_party_share,
            ft.Container(height=5),
            ft.Row([ft.Icon(ft.icons.SYNC_ALT, size=14, color=BLUE_COLOR), r_eq_txt]),
            ft.Row([ft.Icon(ft.icons.CHECK_CIRCLE, size=14, color=ft.colors.GREEN), r_base_txt]),
            ft.Row([ft.Icon(ft.icons.MONETIZATION_ON, size=14, color=ft.colors.RED_400), r_tax_txt]),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
        bgcolor=ft.colors.WHITE,
        border_radius=25,
        padding=25,
        shadow=ft.BoxShadow(blur_radius=20, color=ft.colors.BLACK12, offset=ft.Offset(0, 10)),
        visible=False
    )

    def calc_rent(e):
        mortgage = get_raw_value(mortgage_input.value)
        rent = get_raw_value(rent_input.value)
        if mortgage == 0 and rent == 0: return
        
        total_rent_base = rent + (mortgage * 0.03)
        base = total_rent_base * 0.25 
        tax = base * 0.09
        final_party = base + tax
        
        r_total_income.value = f"{final_party * 2:,.0f} ₸"
        r_party_share.value = f"{final_party:,.0f} تومان"
        r_eq_txt.value = f"اجاره پایه (با تبدیل رهن): {total_rent_base:,.0f} ت"
        r_base_txt.value = f"کمیسیون خالص: {base:,.0f} تومان"
        r_tax_txt.value = f"مالیات (۹٪): {tax:,.0f} تومان"
        
        rent_result_card.visible = True
        page.update()

    rent_view = ft.Column([
        ft.Container(height=5),
        mortgage_container,
        ft.Container(content=mortgage_word_txt, padding=ft.padding.only(right=10)),
        rent_container,
        ft.Container(content=rent_word_txt, padding=ft.padding.only(right=10)),
        ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.icons.CALCULATE), ft.Text("مـحـاسـبـه", size=16, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=BLUE_COLOR, color=ft.colors.WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20), padding=20),
            on_click=calc_rent
        ),
        ft.Container(height=5),
        rent_result_card
    ])

    # ================= منوی تب مدرن بالای صفحه =================
    modern_tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        unselected_label_color=ft.colors.GREY_500,
        label_color=BLUE_COLOR,
        indicator_color=BLUE_COLOR,
        tabs=[
            ft.Tab(text="خرید و فروش", icon=ft.icons.HANDSHAKE, content=ft.Container(content=sale_view, padding=20)),
            ft.Tab(text="رهن و اجاره", icon=ft.icons.HOME_WORK, content=ft.Container(content=rent_view, padding=20)),
        ],
        expand=1,
    )

    page.add(header, modern_tabs)

ft.run(main)
