import re

with open('src/components/EditTradeModal.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    "const [image, setImage] = useState<string | null>(trade.image || null);",
    "const [image, setImage] = useState<string | null>(trade.image || trade.image_url || null);"
)

content = content.replace(
    "import { resizeImage } from '../utils';",
    "import { resizeImage, formatImageUrl } from '../utils';"
)

content = content.replace(
    "<img src={image} className=\"w-full h-full object-cover\" alt=\"After\" />",
    "<img src={formatImageUrl(image)} className=\"w-full h-full object-cover\" alt=\"After\" />"
)

with open('src/components/EditTradeModal.tsx', 'w') as f:
    f.write(content)
