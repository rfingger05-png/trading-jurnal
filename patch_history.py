import re

with open('src/components/History.tsx', 'r') as f:
    content = f.read()

# Replace the condition in History.tsx for rendering the image button
old_img = """                              {trade.image ? (
                                <button
                                   onClick={() => window.open(trade.image, '_blank')}"""

new_img = """                              {(trade.image || trade.image_url) ? (
                                <button
                                   onClick={() => window.open(formatImageUrl(trade.image || trade.image_url), '_blank')}"""

content = content.replace(old_img, new_img)

with open('src/components/History.tsx', 'w') as f:
    f.write(content)
