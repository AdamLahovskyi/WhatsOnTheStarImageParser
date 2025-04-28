from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import customtkinter as ctk
import threading
import webbrowser
from tkinter import Text
from datetime import datetime
import pytz


def scrape_website(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        html = page.content()
        browser.close()
        return html


def extract_clothes_info(html):
    main_image_pattern = r'background-image:\s*url\(&quot;(https://[^&]+)&quot;\)'
    main_image_match = re.search(main_image_pattern, html)

    soup = BeautifulSoup(html, 'html.parser')
    clothes_list = []

    if main_image_match:
        main_image_url = main_image_match.group(1)
        clothes_list.append({
            "brand": "Main Image",
            "name": "Featured Item",
            "price": "",
            "sale_price": None,
            "image_url": main_image_url
        })

    collection_list = soup.find('div', id="collection-list-pc")

    if collection_list:
        items = collection_list.find_all('div', class_="d-flex align-center")
        for item in items:
            brand = item.find('span', class_="brand-name").get_text(strip=True) if item.find('span',
                                                                                             class_="brand-name") else "Unknown Brand"
            name = item.find('span', class_="item-name").get_text(strip=True) if item.find('span',
                                                                                           class_="item-name") else "Unknown Item"
            price = item.find('span', class_="item-price").get_text(strip=True) if item.find('span',
                                                                                             class_="item-price") else "Unknown Price"
            sale_price = item.find('span', class_="item-sale").get_text(strip=True) if item.find('span',
                                                                                                 class_="item-sale") else None

            image_url = None

            cover_image = item.find('div', class_="v-image__image v-image__image--cover")
            if cover_image:
                style = cover_image.get('style')
                if style:
                    patterns = [
                        r'background-image:\s*url\(&quot;(.*?)&quot;\)',
                        r'background-image:\s*url\((.*?)\)',
                        r'url\(&quot;(.*?)&quot;\)',
                        r'url\((.*?)\)'
                    ]

                    for pattern in patterns:
                        match = re.search(pattern, style)
                        if match:
                            image_url = match.group(1)
                            break

            if not image_url:
                image_div = item.find('div', class_="v-image__image")
                if image_div:
                    style = image_div.get('style')
                    if style:
                        patterns = [
                            r'url\(&quot;(.*?)&quot;\)',
                            r'url\((.*?)\)'
                        ]

                        for pattern in patterns:
                            match = re.search(pattern, style)
                            if match:
                                image_url = match.group(1)
                                image_url = image_url.strip('"').strip("'")
                                break

            if image_url:
                image_url = image_url.strip('&quot;').strip('"').strip("'")
                if not image_url.startswith(('http://', 'https://')):
                    image_url = 'https:' + image_url if image_url.startswith('//') else 'https://' + image_url

            clothes_list.append({
                "brand": brand,
                "name": name,
                "price": price,
                "sale_price": sale_price,
                "image_url": image_url
            })
    return clothes_list


def open_link(event):
    try:
        widget = event.widget
        index = widget.index(f"@{event.x},{event.y}")
        tags = widget.tag_names(index)

        for tag in tags:
            if tag.startswith("link_"):
                url = tag[5:]
                webbrowser.open(url)
                break
    except Exception as e:
        print(f"Error opening link: {e}")


def open_social_media(url):
    webbrowser.open(url)


class ModernScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("outonbailswagg")
        self.root.geometry("900x700")

        self.create_ui()

    def create_ui(self):
        self.main_frame = ctk.CTkFrame(self.root, fg_color=("#f0f5ff", "#1a1a2e"))
        self.main_frame.pack(fill="both", expand=True)

        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text="outonbailswagg",
            font=("Arial", 24, "bold"),
            text_color=("#0066cc", "#66a3ff")
        )
        title_label.pack(side="left")

        social_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        social_frame.pack(side="right")

        tiktok_btn = ctk.CTkButton(
            social_frame,
            text="TikTok",
            command=lambda: open_social_media("https://www.tiktok.com/@outonbailswagg"),
            width=100,
            height=30,
            fg_color=("#ff0050", "#ff0050"),
            hover_color=("#cc0040", "#cc0040"),
            font=("Arial", 12, "bold")
        )
        tiktok_btn.pack(side="left", padx=5)

        telegram_btn = ctk.CTkButton(
            social_frame,
            text="Telegram",
            command=lambda: open_social_media("https://t.me/outonbailswagg"),
            width=100,
            height=30,
            fg_color=("#0088cc", "#0088cc"),
            hover_color=("#006699", "#006699"),
            font=("Arial", 12, "bold")
        )
        telegram_btn.pack(side="left", padx=5)

        input_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=10)

        url_label = ctk.CTkLabel(
            input_frame,
            text="Website URL:",
            font=("Arial", 16, "bold")
        )
        url_label.pack(side="left", padx=(0, 10))

        self.url_entry = ctk.CTkEntry(
            input_frame,
            width=500,
            height=40,
            font=("Arial", 14),
            border_width=2,
            corner_radius=8
        )
        self.url_entry.pack(side="left", padx=(0, 10))

        self.fetch_button = ctk.CTkButton(
            input_frame,
            text="Fetch Data",
            command=self.fetch_clothes,
            width=150,
            height=40,
            font=("Arial", 14, "bold"),
            fg_color=("#0066cc", "#3a86ff"),
            hover_color=("#004c99", "#2a65cc"),
            corner_radius=8
        )
        self.fetch_button.pack(side="left")

        status_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        status_frame.pack(fill="x", padx=20, pady=(5, 10))

        status_label = ctk.CTkLabel(
            status_frame,
            text="Status:",
            font=("Arial", 14, "bold")
        )
        status_label.pack(side="left", padx=(0, 10))

        self.status_value = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=("Arial", 14),
            text_color=("#4d4d4d", "#a6a6a6")
        )
        self.status_value.pack(side="left")

        results_frame = ctk.CTkFrame(self.main_frame, fg_color=("white", "#121212"), corner_radius=10)
        results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        results_label = ctk.CTkLabel(
            results_frame,
            text="Results",
            font=("Arial", 16, "bold"),
            anchor="w"
        )
        results_label.pack(fill="x", padx=15, pady=(15, 5))

        appearance_mode = ctk.get_appearance_mode().lower()
        bg_color = "#121212" if appearance_mode == "dark" else "white"
        fg_color = "#e6e6e6" if appearance_mode == "dark" else "black"

        self.result_text = Text(
            results_frame,
            wrap="word",
            font=("Consolas", 12),
            bg=bg_color,
            fg=fg_color,
            height=20,
            borderwidth=0,
            padx=15,
            pady=10
        )

        self.result_text.tag_configure("timestamp", foreground="#666666", font=("Consolas", 12, "italic"))
        self.result_text.tag_configure("user_info", foreground="#666666", font=("Consolas", 12, "italic"))
        self.result_text.tag_configure("label", foreground="#0066cc", font=("Consolas", 12, "bold"))
        self.result_text.tag_configure("value", foreground=fg_color, font=("Consolas", 12))
        self.result_text.tag_configure("error", foreground="#ff0000", font=("Consolas", 12, "bold"))
        self.result_text.tag_configure("separator", foreground="#cccccc")
        self.result_text.tag_configure("link", foreground="#0000ff", underline=1)

        self.result_text.bind("<Button-1>", open_link)

        scrollbar = ctk.CTkScrollbar(results_frame, command=self.result_text.yview)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
        self.result_text.configure(yscrollcommand=scrollbar.set)

        self.result_text.pack(fill="both", expand=True, padx=10, pady=10, side="left")

        self.update_text_colors()
        self.root.bind("<<AppearanceModeChanged>>", self.update_text_colors)

    def update_text_colors(self, event=None):
        appearance_mode = ctk.get_appearance_mode().lower()
        bg_color = "#121212" if appearance_mode == "dark" else "white"
        fg_color = "#e6e6e6" if appearance_mode == "dark" else "black"

        self.result_text.configure(bg=bg_color, fg=fg_color)
        self.result_text.tag_configure("value", foreground=fg_color)

    def fetch_clothes(self):
        self.status_value.configure(text="Loading...", text_color=("#ff9900", "#ffcc00"))
        self.fetch_button.configure(state="disabled")

        def scraping_task():
            url = self.url_entry.get()
            if not url:
                self.result_text.delete("1.0", "end")
                self.result_text.insert("end", "Error: Please enter a valid URL\n", "error")
                self.status_value.configure(text="Error", text_color=("#ff0000", "#ff3333"))
                self.fetch_button.configure(state="normal")
                return

            try:
                html = scrape_website(url)
                clothes = extract_clothes_info(html)

                self.result_text.delete("1.0", "end")

                current_time = datetime.now(pytz.UTC).strftime("Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): %Y-%m-%d %H:%M:%S")
                self.result_text.insert("end", f"{current_time}\n", "timestamp")
                self.result_text.insert("end", f"Current User's Login: AdamLahovskyi\n\n", "user_info")

                if clothes:
                    for item in clothes:
                        self.result_text.insert("end", f"Brand: ", "label")
                        self.result_text.insert("end", f"{item['brand']}\n", "value")

                        self.result_text.insert("end", f"Name: ", "label")
                        self.result_text.insert("end", f"{item['name']}\n", "value")

                        self.result_text.insert("end", f"Price: ", "label")
                        self.result_text.insert("end", f"{item['price']}\n", "value")

                        if item['sale_price']:
                            self.result_text.insert("end", f"Sale Price: ", "label")
                            self.result_text.insert("end", f"{item['sale_price']}\n", "value")

                        if item['image_url']:
                            self.result_text.insert("end", f"Image URL: ", "label")
                            url = item['image_url'].strip('&quot;')
                            self.result_text.insert("end", url + "\n", (f"link_{url}", "link"))

                        self.result_text.insert("end", "─" * 50 + "\n", "separator")
                else:
                    self.result_text.insert("end", "No clothes found on the page.", "error")

                self.status_value.configure(text="Completed", text_color=("#00cc66", "#33ff99"))
            except Exception as e:
                self.result_text.delete("1.0", "end")
                self.result_text.insert("end", f"Error: {str(e)}\n", "error")
                self.status_value.configure(text="Error", text_color=("#ff0000", "#ff3333"))
            finally:
                self.fetch_button.configure(state="normal")

        threading.Thread(target=scraping_task).start()


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    scraper = ModernScraperApp(app)
    app.mainloop()