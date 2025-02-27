import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import requests
from bs4 import BeautifulSoup
import pandas as pd
import threading
import os
import re
import time

class WebScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Scraper Pro")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        self.primary_color = "#3498db"  # Blue
        self.secondary_color = "#2ecc71"  # Green
        self.bg_color = "#f5f5f5"  # Light gray
        self.text_color = "#333333"  # Dark gray
        self.accent_color = "#e74c3c"  # Red
        
        self.data_type_var = tk.StringVar(value="Paragraphs")
        self.status_var = tk.StringVar(value="Ready")
        self.scraped_data = []
        self.total_items_var = tk.StringVar(value="Total items: 0")
        self.data_type_desc_var = tk.StringVar(value="Extract all paragraph text from the webpage")
        
        self.root.configure(bg=self.bg_color)
        
        self.configure_styles()
        
        self.main_frame = ttk.Frame(self.root, style="Main.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.create_header()
        
        self.create_content_area()
        
        self.create_status_bar()
        
    def configure_styles(self):
        self.style = ttk.Style()
        
        self.style.configure("Main.TFrame", background=self.bg_color)
        self.style.configure("Card.TFrame", background="white", relief="raised")
        
        self.style.configure("Header.TLabel", 
                            font=("Helvetica", 18, "bold"),
                            background=self.bg_color, 
                            foreground=self.primary_color)
        
        self.style.configure("SubHeader.TLabel", 
                            font=("Helvetica", 14, "bold"),
                            background="white", 
                            foreground=self.text_color)
        
        self.style.configure("Normal.TLabel", 
                            font=("Helvetica", 12),
                            background="white", 
                            foreground=self.text_color)
        
        self.style.configure("Status.TLabel", 
                            font=("Helvetica", 10),
                            background="#f0f0f0", 
                            foreground=self.text_color)
        
        self.style.configure("Primary.TButton", 
                            font=("Helvetica", 12, "bold"),
                            background=self.primary_color, 
                            foreground="white")
        
        self.style.configure("Success.TButton", 
                            font=("Helvetica", 12, "bold"),
                            background=self.secondary_color, 
                            foreground="white")
        
        self.style.map("Primary.TButton",
                      background=[("active", "#2980b9")],
                      foreground=[("active", "white")])
        
        self.style.map("Success.TButton",
                      background=[("active", "#27ae60")],
                      foreground=[("active", "white")])
                      
        self.style.configure("TCombobox", 
                            font=("Helvetica", 12),
                            foreground=self.text_color)
        
        self.style.configure("TProgressbar", 
                            thickness=20,
                            background=self.secondary_color)
        
    def create_header(self):
        header_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, 
                               text="Web Scraper Pro", 
                               style="Header.TLabel")
        title_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(header_frame, 
                                 text="v2.0",
                                 style="Header.TLabel")
        version_label.pack(side=tk.RIGHT)
        
    def create_content_area(self):
        url_card = ttk.Frame(self.main_frame, style="Card.TFrame")
        url_card.pack(fill=tk.X, pady=10, padx=5, ipady=10)
        
        url_header = ttk.Label(url_card, 
                              text="Website URL", 
                              style="SubHeader.TLabel")
        url_header.pack(anchor=tk.W, padx=15, pady=(15, 5))
        
        url_desc = ttk.Label(url_card, 
                            text="Enter the complete URL of the website you want to scrape", 
                            style="Normal.TLabel")
        url_desc.pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        url_frame = ttk.Frame(url_card, style="Card.TFrame")
        url_frame.pack(fill=tk.X, padx=15, pady=5)
        
        self.url_entry = ttk.Entry(url_frame, 
                                  font=("Helvetica", 12), 
                                  width=50)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.validate_button = ttk.Button(url_frame, 
                                        text="Validate URL", 
                                        style="Primary.TButton",
                                        command=self.validate_url)
        self.validate_button.pack(side=tk.RIGHT)
        
        options_card = ttk.Frame(self.main_frame, style="Card.TFrame")
        options_card.pack(fill=tk.X, pady=10, padx=5, ipady=10)
        
        options_header = ttk.Label(options_card, 
                                  text="Scraping Options", 
                                  style="SubHeader.TLabel")
        options_header.pack(anchor=tk.W, padx=15, pady=(15, 10))
        
        data_type_frame = ttk.Frame(options_card, style="Card.TFrame")
        data_type_frame.pack(fill=tk.X, padx=15, pady=5)
        
        data_type_label = ttk.Label(data_type_frame, 
                                   text="Data Type:", 
                                   style="Normal.TLabel",
                                   width=15)
        data_type_label.pack(side=tk.LEFT, padx=(0, 10))
        
        data_types = [
            ("Paragraphs", "paragraphs"),
            ("Headings", "headings"),
            ("Links", "links"),
            ("Images", "images"),
            ("Tables", "tables")
        ]
        
        data_type_menu = ttk.Combobox(data_type_frame, 
                                     textvariable=self.data_type_var,
                                     values=[dt[0] for dt in data_types],
                                     state="readonly",
                                     font=("Helvetica", 12),
                                     width=30)
        data_type_menu.pack(side=tk.LEFT, fill=tk.X, expand=True)
        data_type_menu.current(0)
        
        data_type_menu.bind("<<ComboboxSelected>>", self.update_data_type_description)
        
        self.data_type_desc = ttk.Label(options_card, 
                                       textvariable=self.data_type_desc_var, 
                                       style="Normal.TLabel",
                                       wraplength=700)
        self.data_type_desc.pack(anchor=tk.W, padx=15, pady=(5, 15))
        
        action_card = ttk.Frame(self.main_frame, style="Card.TFrame")
        action_card.pack(fill=tk.X, pady=10, padx=5, ipady=10)
        
        self.progress_frame = ttk.Frame(action_card, style="Card.TFrame")
        self.progress_frame.pack(fill=tk.X, padx=15, pady=10)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, 
                                           style="TProgressbar", 
                                           orient="horizontal", 
                                           length=100, 
                                           mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=(10, 5))
        
        self.progress_label = ttk.Label(self.progress_frame, 
                                       text="Ready to scrape", 
                                       style="Normal.TLabel")
        self.progress_label.pack(anchor=tk.W)
        
        self.progress_frame.pack_forget()
        
        button_frame = ttk.Frame(action_card, style="Card.TFrame")
        button_frame.pack(fill=tk.X, padx=15, pady=10)
        
        self.total_items_label = ttk.Label(button_frame, 
                                          textvariable=self.total_items_var,
                                          style="Normal.TLabel")
        self.total_items_label.pack(side=tk.LEFT)
        
        self.scrape_button = ttk.Button(button_frame, 
                                       text="Start Scraping", 
                                       style="Success.TButton",
                                       command=self.start_scraping)
        self.scrape_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.clear_button = ttk.Button(button_frame, 
                                      text="Clear", 
                                      style="Primary.TButton",
                                      command=self.clear_form)
        self.clear_button.pack(side=tk.RIGHT)
        
    def create_status_bar(self):
        status_bar = ttk.Frame(self.root, relief=tk.SUNKEN, style="Main.TFrame")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        status_label = ttk.Label(status_bar, 
                                textvariable=self.status_var, 
                                style="Status.TLabel",
                                padding=(10, 5))
        status_label.pack(side=tk.LEFT, fill=tk.X)
    
    def update_data_type_description(self, event=None):
        selected = self.data_type_var.get()
        descriptions = {
            "Paragraphs": "Extract all paragraph text from the webpage",
            "Headings": "Extract all headings (H1-H6) from the webpage",
            "Links": "Extract all hyperlinks (URLs) from the webpage",
            "Images": "Extract all image sources from the webpage",
            "Tables": "Extract all table data from the webpage"
        }
        self.data_type_desc_var.set(descriptions.get(selected, ""))
    
    def validate_url(self):
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return False
        
        if not url.startswith(('http://', 'https://')):
            messagebox.showerror("Error", "URL must start with http:// or https://")
            return False
        
        url_pattern = re.compile(
            r'^(?:http|https)://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or ipv4
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            messagebox.showerror("Error", "Invalid URL format")
            return False
            
        self.status_var.set("Testing connection...")
        self.root.update()
        
        try:
            response = requests.head(url, timeout=5)
            if response.status_code >= 400:
                messagebox.showwarning("Warning", f"URL returned status code {response.status_code}. It may not be accessible.")
                self.status_var.set("Ready")
                return False
                
            messagebox.showinfo("Success", "URL is valid and accessible")
            self.status_var.set("URL validated successfully")
            return True
            
        except requests.RequestException as e:
            messagebox.showerror("Connection Error", f"Could not connect to the URL: {str(e)}")
            self.status_var.set("Ready")
            return False
    
    def clear_form(self):
        self.url_entry.delete(0, tk.END)
        self.data_type_var.set("Paragraphs")
        self.update_data_type_description()
        self.progress_frame.pack_forget()
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Ready to scrape")
        self.total_items_var.set("Total items: 0")
        self.scraped_data = []
        self.status_var.set("Ready")
    
    def start_scraping(self):
        if not self.validate_url():
            return
        
        url = self.url_entry.get().strip()
        data_type_display = self.data_type_var.get()
        
        data_type_map = {
            "Paragraphs": "paragraphs",
            "Headings": "headings",
            "Links": "links",
            "Images": "images",
            "Tables": "tables"
        }
        data_type = data_type_map.get(data_type_display, "paragraphs")
        
        self.progress_frame.pack(fill=tk.X, padx=15, pady=10)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Initializing scraper...")
        
        self.url_entry.config(state=tk.DISABLED)
        self.scrape_button.config(state=tk.DISABLED)
        self.validate_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
        
        self.status_var.set(f"Scraping {data_type_display.lower()} from {url}")
        
        threading.Thread(target=self.process_scraping, args=(url, data_type)).start()
    
    def process_scraping(self, url, data_type):
        try:
            self.update_progress(10, "Connecting to website...")
            
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                self.show_error(f"Failed to retrieve webpage (Status code: {response.status_code})")
                return
            
            self.update_progress(30, "Parsing webpage content...")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            self.update_progress(50, f"Extracting {data_type}...")
            
            self.scraped_data = self.extract_data(soup, data_type)
            
            self.update_progress(80, "Processing extracted data...")
            time.sleep(0.5)  
            
            self.total_items_var.set(f"Total items: {len(self.scraped_data)}")
            
            self.update_progress(100, "Scraping completed!")
            
            if self.scraped_data:
                self.root.after(500, self.prompt_save)
            else:
                messagebox.showinfo("No Data", f"No {data_type} found on the webpage.")
                self.reset_ui()
                
        except Exception as e:
            self.show_error(f"An error occurred while scraping: {str(e)}")
    
    def extract_data(self, soup, data_type):
        data = []
        
        try:
            if data_type == 'paragraphs':
                for paragraph in soup.find_all('p'):
                    text = paragraph.get_text(strip=True)
                    if text:
                        data.append({'Paragraph Text': text})
                        
            elif data_type == 'headings':
                for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    text = heading.get_text(strip=True)
                    if text:
                        heading_type = heading.name
                        data.append({'Heading Type': heading_type, 'Heading Text': text})
                        
            elif data_type == 'links':
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    if href:
                        data.append({'Link Text': text or '[No text]', 'Link URL': href})
                        
            elif data_type == 'images':
                for img in soup.find_all('img', src=True):
                    src = img.get('src')
                    alt = img.get('alt', '')
                    if src:
                        data.append({'Image Source': src, 'Alt Text': alt})
                        
            elif data_type == 'tables':
                tables = soup.find_all('table')
                for i, table in enumerate(tables):
                    rows = table.find_all('tr')
                    for row_index, row in enumerate(rows):
                        cells = row.find_all(['td', 'th'])
                        cell_data = [cell.get_text(strip=True) for cell in cells]
                        if cell_data:
                            data.append({
                                'Table Index': i + 1,
                                'Row Index': row_index + 1,
                                'Row Data': cell_data
                            })
            return data
            
        except Exception as e:
            messagebox.showerror("Error", f"Error extracting data: {str(e)}")
            return []
    
    def update_progress(self, value, message):
        self.root.after(0, lambda: self._update_progress_ui(value, message))
    
    def _update_progress_ui(self, value, message):
        self.progress_bar['value'] = value
        self.progress_label.config(text=message)
        self.root.update_idletasks()
    
    def show_error(self, message):
        self.root.after(0, lambda: self._show_error_ui(message))
    
    def _show_error_ui(self, message):
        messagebox.showerror("Error", message)
        self.reset_ui()
    
    def reset_ui(self):
        self.url_entry.config(state=tk.NORMAL)
        self.scrape_button.config(state=tk.NORMAL)
        self.validate_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)
        self.status_var.set("Ready")
        
        self.progress_frame.pack_forget()
    
    def prompt_save(self):
        if messagebox.askyesno("Save Data", f"Successfully scraped {len(self.scraped_data)} items. Would you like to save the data?"):
            self.save_data()
        self.reset_ui()
    
    def save_data(self):
        filename = filedialog.asksaveasfilename(
            defaultextension='.xlsx',
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ],
            title="Save Scraped Data"
        )
        
        if not filename:
            return
        
        try:
            df = pd.DataFrame(self.scraped_data)
            
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext == '.xlsx':
                df.to_excel(filename, index=False)
                
            elif file_ext == '.csv':
                df.to_csv(filename, index=False)
                
            elif file_ext == '.json':
                df.to_json(filename, orient='records', indent=4)
                
            else:
                df.to_excel(filename, index=False)
            
            messagebox.showinfo("Success", f"Data has been saved to '{filename}'")
            self.status_var.set(f"Data saved to {os.path.basename(filename)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = WebScraperApp(root)
    root.mainloop()
