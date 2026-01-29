import requests
import json
import sys

API_BASE_URL = "http://localhost:8001/api"

product_data = {
    "title": "Sony WH-1000XM6 The Best Noise Canceling Wireless Headphones, HD NC Processor QN3, 12 Microphones, Adaptive NC Optimizer, Mastered by Engineers, Studio-Quality, 30-Hour Battery, Black",
    "description": """THE BEST NOISE CANCELLATION: Powered by advanced processors and an adaptive microphone system, the WH-1000XM6 headphones deliver real-time noise cancellation for an immersive, distraction-free listening experience.
CO-CREATED WITH MASTERING AUDIO ENGINEERS: Developed in collaboration with world-renowned mastering audio engineers, these headphones deliver unparalleled sound clarity and precision. A specially designed driver with a lightweight carbon fiber dome delivers high fidelity sound, where rich vocals and every instrument remains pure and balanced. Optimized for advanced noise cancellation, the WH-1000XM6 headphones keep every frequency crisp and true to the artist’s intent.
HD NOISE CANCELING PROCESSOR QN3: The HD Noise Canceling Processor QN3 is 7x faster than the QN1 (found in our WH-1000XM5 headphones), optimizing 12 microphones in real time for superior noise cancellation, sound quality, and call clarity. With more microphones than ever, we can precisely detect external noise and counteracts it with opposite soundwaves, delivering a new level of noise cancellation.
ULTRA-CLEAR CALLS, FROM ANYWHERE: A six-microphone AI-based beamforming system, intelligent noise reduction technology, and wind-resistant design, work together to isolate your voice, filter out background noise, and ensure every word comes through crisp and clear—even in the busiest environments.
COMPACT CARRYING CASE & FOLDABLE DESIGN: Crafted for durability and style, the foldable design features precision metalwork and a compact case with a magnetic closure—ready to go wherever you do.
TAILORED COMFORT, THOUGHTFULLY DESIGNED: A wider, asymmetrical headband with smooth synthetic leather ensures a pressure-free, all-day fit, while a stepless slider and seamless swivel make every adjustment effortless.
LONG BATTERY LIFE AND CONVENIENT CHARGING: With up to 30 hours of battery life, these headphones ensure you’re powered for even the longest trips. When you’re running low, simply plug in the USB charging cable and keep listening, with both Bluetooth and audio cable connections supported. Charge for 3 minutes and you’ll get up to 3 hours of playback with an optional USB-PD compatible AC adapter.
ADAPTIVE NC OPTIMIZER: Our new Adaptive NC Optimizer intelligently adjusts to a variety of factors, including external noise, air pressure, and your wearing style, even while wearing a hat or glasses, for uninterrupted, immersive sound. This technology monitors your environment to ensure you enjoy the purest, most immersive sound, no matter where you are.
AUTO AMBIENT SOUND MODE: Our Auto Ambient Sound mode adapts to your surroundings in real time by balancing music and external sound. The multiple microphones can filter out the noise or let in what matters: announcements, conversations, or the world around you.
HIGH-RESOLUTION AUDIO: The WH-1000XM6 headphones support High-Resolution Audio and High-Resolution Audio Wireless, thanks to LDAC, our industry-adopted audio coding technology. LDAC transmits approximately three times more data than conventional Bluetooth audio for exceptional High-Resolution Audio quality.""",
    "category": "Headphones",
    "brand": "Sony"
}

try:
    response = requests.post(f"{API_BASE_URL}/analyze-product", json=product_data)
    result = response.json()
    print(json.dumps(result['score_breakdown'], indent=2))
    print(f"SCORE: {result['ai_visibility_score']}")
except Exception as e:
    print(f"ERROR: {e}")
