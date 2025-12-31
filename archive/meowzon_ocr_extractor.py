#!/usr/bin/env python3

"""
Meowzon Order OCR Extractor - Cat-Themed Edition v2.0

Now with HYBRID AI SUPPORT! 🐾
- Traditional Tesseract + OpenCV (fast, local)
- Optional AI fallback/always for superior structured extraction
- Supported AI providers: Ollama (local), OpenAI (cloud, GPT-4o)
- Best of both worlds: Tesseract first, AI on failure or always
- Still aggressive cropping + enhanced image saving
"""

import os
import re
import cv2
import numpy as np
import pytesseract
import pandas as pd
from tqdm import tqdm
import argparse
import sys
import platform
import base64
import json
import requests  # For Ollama

# Optional for OpenAI
try:
    from openai import OpenAI as OpenAIClient
except ImportError:
    OpenAIClient = None

# ----------------------------- AUTO TESSERACT PATH (Windows) -----------------------------
if platform.system() == "Windows":
    default_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(default_tesseract):
        pytesseract.pytesseract.tesseract_cmd = default_tesseract

# ----------------------------- CAT BANNER -----------------------------
def print_banner():
    banner = """
\033[1;35m
      /\\_/\\      ███╗   ███╗███████╗ ██████╗ ██╗    ██╗███████╗ ██████╗ ███╗   ██╗
     ( o.o )     ████╗ ████║██╔════╝██╔═══██╗██║    ██║╚══███╔╝██╔═══██╗████╗  ██║
      > ^ <      ██╔████╔██║█████╗  ██║   ██║██║ █╗ ██║  ███╔╝ ██║   ██║██╔██╗ ██║
                 ██║╚██╔╝██║██╔══╝  ██║   ██║██║███╗██║ ███╔╝  ██║   ██║██║╚██╗██║
      /\\_/\\      ██║ ╚═╝ ██║███████╗╚██████╔╝╚███╔███╔╝███████╗╚██████╔╝██║ ╚████║
     ( o.o )     ╚═╝     ╚═╝╚══════╝ ╚═════╝  ╚══╝╚══╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝
      > ^ <               ██████╗ ██████╗ ██████╗     ███████╗██╗  ██╗████████╗██████╗  █████╗  ██████╗████████╗ ██████╗ ██████╗ 
                          ██╔═══██╗██╔═══██╗██╔══██╗    ██╔════╝╚██╗██╔╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝██╔═══██╗██╔══██╗
                          ██║   ██║██║   ██║██████╔╝    █████╗   ╚███╔╝    ██╔╝   ██████╔╝███████║██║     ██████╔╝██║   ██║██████╔╝
                          ██║   ██║██║   ██║██╔══██╗    ██╔══╝   ██╔██╔╝    ██╔╝   ██╔══██╗██╔══██║██║     ██╔══██╗██║   ██║██╔══██╗
                          ╚██████╔╝╚██████╔╝██║  ██║    ███████╗██╔╝ ██╔╝    ██║    ██║  ██║██║  ██║╚██████╔╝██║  ╚██╗╚██████╔╝██║  ██║
                           ╚═════╝  ╚═════╝ ╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═╝     ╚═╝    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
\033[0m
    """
    print(banner)
    print("\033[1;36m😺 Meowzon Order OCR Extractor v2.0 - AI Hybrid Edition 😺\033[0m")
    print("\033[90mUltimate extraction with Tesseract + optional AI vision models!\033[0m\n")

# ----------------------------- CROPPING STRATEGIES -----------------------------
additional_crops = [
    {"name": "No Bottom 20%", "top": 0.0, "bottom": 0.2, "left": 0.0, "right": 0.0},
    {"name": "No Top 20%", "top": 0.2, "bottom": 0.0, "left": 0.0, "right": 0.0},
    {"name": "No Top 15%", "top": 0.15, "bottom": 0.0, "left": 0.0, "right": 0.0},
    {"name": "Center 80%", "top": 0.1, "bottom": 0.1, "left": 0.1, "right": 0.1},
    {"name": "Tight Center", "top": 0.1, "bottom": 0.1, "left": 0.05, "right": 0.05},
]

# ----------------------------- PREPROCESS FOR TESSERACT -----------------------------
def preprocess_for_tesseract(color_img):
    gray = cv2.cvtColor(color_img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15)
    inv_thresh = cv2.bitwise_not(thresh)
    config = '--psm 6 --oem 3'

    def ocr_with_conf(image):
        try:
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, config=config)
            confs = [int(c) for c in data['conf'] if c != '-1']
            mean_conf = np.mean(confs) if confs else 0
            text = pytesseract.image_to_string(image, config=config)
            return text.strip(), mean_conf
        except:
            return "", 0.0

    text_normal, conf_normal = ocr_with_conf(thresh)
    text_inv, conf_inv = ocr_with_conf(inv_thresh)

    if conf_normal >= conf_inv:
        return text_normal, conf_normal, thresh
    else:
        return text_inv, conf_inv, inv_thresh

# ----------------------------- TRIAL CROPPING (returns best color + processed) -----------------------------
def get_best_image(file_path):
    img = cv2.imread(file_path)
    if img is None:
        return None, "", 0.0, "Failed", "Full Image", None

    # Full image first
    text, conf, proc_img = preprocess_for_tesseract(img)
    crop_name = "Full Image"
    best_color = img
    best_proc = proc_img
    best_conf = conf
    best_text = text
    best_crop_params = None

    score = conf + 100 if re.search(r'\d{3}-\d{7}-\d{7}', text) else 0

    for crop_dict in additional_crops:
        h, w = img.shape[:2]
        start_y = int(h * crop_dict["top"])
        end_y = h - int(h * crop_dict["bottom"])
        start_x = int(w * crop_dict["left"])
        end_x = w - int(w * crop_dict["right"])
        if end_y <= start_y or end_x <= start_x:
            continue
        cropped = img[start_y:end_y, start_x:end_x]
        t_text, t_conf, t_proc = preprocess_for_tesseract(cropped)
        t_score = t_conf + 100 if re.search(r'\d{3}-\d{7}-\d{7}', t_text) else 0
        if t_score > score:
            score = t_score
            best_text = t_text
            best_conf = t_conf
            best_color = cropped
            best_proc = t_proc
            crop_name = crop_dict["name"]
            best_crop_params = crop_dict

    return best_color, best_text, best_conf, crop_name, best_proc, best_crop_params

# ----------------------------- TRADITIONAL EXTRACTION -----------------------------
def extract_with_tesseract(text):
    order_ids = list(set(re.findall(r'\d{3}-\d{7}-\d{7}', text)))
    prices = re.findall(r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?', text)
    dates = re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}', text)
    totals = re.findall(r'(?:Order Total|Grand Total|Total)[\s:]*(\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', text, re.IGNORECASE)
    quantities = re.findall(r'(?:Qty|Quantity)[\.:]?\s*(\d+)', text, re.IGNORECASE)
    sellers = list(set(re.findall(r'Sold by[:\s]*(.+?)(?:\n|$)', text)))
    lines = [l.strip() for l in text.split('\n') if l.strip() and len(l) > 10]
    items = []
    for line in lines:
        clean = re.sub(r'\$[\d,]+\.?\d*|\d{3}-\d{7}.*', '', line).strip()
        if len(clean) > 15 and clean[0].isupper() and not re.search(r'total|shipping|tax|qty|sold by', clean, re.IGNORECASE):
            items.append(clean)
    items = list(set(items))
    return order_ids, prices, dates, totals, quantities, sellers, items

# ----------------------------- AI EXTRACTION -----------------------------
def extract_with_ai(image_path, provider, ollama_model="llava", openai_model="gpt-4o-mini"):
    with open(image_path, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read()).decode('utf-8')

    prompt = """
You are an expert Amazon order analyst. Extract structured data from this screenshot as VALID JSON ONLY (no extra text or markdown):

{
  "order_id": "string or null",
  "order_date": "string or null",
  "total": "string or null",
  "items": [
    {
      "name": "string",
      "quantity": integer or null,
      "price": "string or null"
    }
  ],
  "seller": "string or null",
  "other_prices": array of strings
}

If no data found, use null/empty. Be precise.
"""

    if provider == "ollama":
        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": ollama_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt,
                            "images": [base64_image]
                        }
                    ],
                    "stream": False
                }
            )
            response.raise_for_status()
            content = response.json()["message"]["content"]
        except Exception as e:
            print(f"\033[91mOllama error: {e}\033[0m")
            return None

    elif provider == "openai":
        if OpenAIClient is None:
            print("\033[91mOpenAI library not installed. pip install openai\033[0m")
            return None
        try:
            client = OpenAIClient()
            response = client.chat.completions.create(
                model=openai_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }
                ],
                max_tokens=500
            )
            content = response.choices[0].message.content
        except Exception as e:
            print(f"\033[91mOpenAI error: {e} (check API key)\033[0m")
            return None

    # Parse JSON
    try:
        data = json.loads(content)
        # Normalize to lists/strings
        order_ids = [data.get("order_id")] if data.get("order_id") else []
        dates = [data.get("order_date")] if data.get("order_date") else []
        totals = [data.get("total")] if data.get("total") else []
        items = [i["name"] for i in data.get("items", []) if i.get("name")]
        quantities = [str(i.get("quantity") or "") for i in data.get("items", [])]
        sellers = [data.get("seller")] if data.get("seller") else []
        prices = data.get("other_prices", []) + [i.get("price") for i in data.get("items", []) if i.get("price")]
        return order_ids, prices, dates, totals, quantities, sellers, items, "AI Success"
    except:
        return None, None, None, None, None, None, None, "AI JSON Parse Failed"

# ----------------------------- MAIN -----------------------------
def main():
    print_banner()

    parser = argparse.ArgumentParser(description="😺 Ultimate Amazon order extractor with AI hybrid")
    parser.add_argument('-i', '--input', default='./screenshots', help='Input folder')
    parser.add_argument('-o', '--output', default='meowzon_orders.csv', help='Output CSV')
    parser.add_argument('--aggressive', action='store_true', help='Auto-crop + save enhanced images')
    parser.add_argument('--use-ai', choices=['never', 'hybrid', 'always'], default='never', help='AI mode: never, hybrid (fallback), always')
    parser.add_argument('--ai-provider', choices=['ollama', 'openai'], default='ollama', help='AI backend')
    parser.add_argument('--ollama-model', default='llava', help='Ollama model (e.g., qwen2-vl:7b, llava:13b)')
    parser.add_argument('--openai-model', default='gpt-4o-mini', help='OpenAI model (gpt-4o-mini or gpt-4o)')
    args = parser.parse_args()

    if args.use_ai != 'never':
        print(f"\033[1m😼 AI mode: {args.use_ai.upper()} | Provider: {args.ai_provider.upper()}\033[0m\n")

    if args.aggressive:
        enhanced_folder = "meowzon_enhanced_images"
        os.makedirs(enhanced_folder, exist_ok=True)

    # Tesseract check
    try:
        pytesseract.get_tesseract_version()
    except:
        print("\033[91mTesseract not found!\033[0m")
        sys.exit(1)

    folder_path = args.input
    if not os.path.exists(folder_path):
        print(f"\033[91mFolder not found: {folder_path}\033[0m")
        sys.exit(1)

    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not files:
        print("\033[93mNo images found!\033[0m")
        sys.exit(0)

    all_data = []

    for filename in tqdm(files, desc="Purr-cessing", unit="paw"):
        file_path = os.path.join(folder_path, filename)

        best_color, tess_text, tess_conf, crop_used, best_proc, crop_params = get_best_image(file_path)

        if best_color is None:
            status = "Failed Load"
            all_data.append({"File Name": filename, "Status": status})
            continue

        # Tesseract extraction
        orders, prices, dates, totals, qtys, sellers, items = extract_with_tesseract(tess_text)

        ai_used = False
        ai_provider = ""
        ai_status = ""

        # Decide if to use AI
        use_ai_now = (args.use_ai == 'always') or (args.use_ai == 'hybrid' and (tess_conf < 70 or not orders))

        if use_ai_now:
            # Save temp image for AI (original color, cropped if better)
            temp_img_path = os.path.join("temp_ai_image.jpg")
            cv2.imwrite(temp_img_path, best_color)

            ai_orders, ai_prices, ai_dates, ai_totals, ai_qtys, ai_sellers, ai_items, ai_status = extract_with_ai(
                temp_img_path, args.ai_provider, args.ollama_model, args.openai_model
            )
            os.remove(temp_img_path)

            if ai_orders is not None:
                # Prefer AI results
                orders, prices, dates, totals, qtys, sellers, items = ai_orders, ai_prices, ai_dates, ai_totals, ai_qtys, ai_sellers, ai_items
                ai_used = True
                ai_provider = args.ai_provider

        # Save enhanced images if aggressive
        cropped_file = processed_file = ""
        if args.aggressive:
            base, ext = os.path.splitext(filename)
            if crop_used != "Full Image":
                safe_crop = crop_used.replace(' ', '_')
                cropped_file = f"{base}_cropped_{safe_crop}{ext}"
                cv2.imwrite(os.path.join(enhanced_folder, cropped_file), best_color)
            processed_file = f"{base}_processed{ext}"
            cv2.imwrite(os.path.join(enhanced_folder, processed_file), best_proc)

        # Status
        status = "\033[92mSuccess 🐾\033[0m" if orders else "\033[93mReview Required 🙀\033[0m"
        if crop_used != "Full Image":
            status += f" \033[90m(Cropped: {crop_used})\033[0m"
        if ai_used:
            status += f" \033[96m(AI: {ai_provider.upper()} {ai_status})\033[0m"

        print(f"[{status}] {filename} → {len(orders)} order(s), {len(items)} item(s), conf: {tess_conf:.1f}%")

        all_data.append({
            "File Name": filename,
            "Status": status.replace("\033[", "").split("m")[0],
            "AI Used": "Yes" if ai_used else "No",
            "AI Provider": ai_provider,
            "Tesseract Confidence (%)": round(tess_conf, 1),
            "Crop Used": crop_used,
            "Cropped Image": cropped_file,
            "Processed Image": processed_file,
            "Order IDs": " | ".join(orders),
            "Prices": " | ".join(prices),
            "Dates": " | ".join(dates),
            "Totals": " | ".join(totals),
            "Quantities": " | ".join(qtys),
            "Sellers": " | ".join(sellers),
            "Items": " | ".join(items),
            "Raw Tesseract Snippet": tess_text[:200] + "..." if len(tess_text) > 200 else tess_text
        })

    df = pd.DataFrame(all_data)
    df.to_csv(args.output, index=False)
    print(f"\n\033[1;32mDone! CSV: {args.output} 🐈\033[0m")
    if args.aggressive:
        print(f"\033[1;32mEnhanced images in '{enhanced_folder}/'\033[0m")

if __name__ == "__main__":
    main()
