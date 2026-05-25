import requests
import os
import matplotlib.pyplot as plt
from datetime import datetime
import tweepy
from dotenv import load_dotenv

load_dotenv()

# ==================== 설정 ====================
KPX_SERVICE_KEY = os.getenv('KPX_SERVICE_KEY')
X_API_KEY = os.getenv('X_API_KEY')
X_API_SECRET = os.getenv('X_API_SECRET')
X_ACCESS_TOKEN = os.getenv('X_ACCESS_TOKEN')
X_ACCESS_SECRET = os.getenv('X_ACCESS_SECRET')

# ==================== 데이터 가져오기 ====================
def get_power_data():
    url = "http://apis.data.go.kr/B552115/TotElecPowerStatusService/getTotElecPowerStatus"
    params = {
        'serviceKey': KPX_SERVICE_KEY,
        'numOfRows': 1,
        'pageNo': 1,
        'dataType': 'JSON',
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        item = data['response']['body']['items']['item'][0]
        
        return {
            'baseDate': item.get('baseDate', ''),
            'supply': int(item.get('supply', 0)),
            'demand': int(item.get('demand', 0)),
            'reserve': int(item.get('reserve', 0)),
            'reserveRate': float(item.get('reserveRate', 0))
        }
    except Exception as e:
        print("API 오류:", e)
        return None

# ==================== 그래프 생성 ====================
def create_graph(data):
    if not data:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 6))
    categories = ['공급능력', '현재수요', '예비력']
    values = [data['supply'], data['demand'], data['reserve']]
    
    bars = ax.bar(categories, values, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 500,
                f'{height:,} MW', ha='center', va='bottom', fontsize=11)
    
    ax.set_ylabel('전력 (MW)', fontsize=12)
    ax.set_title(f'전력시장 현황 ({data["baseDate"]})', fontsize=14, pad=20)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    filename = 'power_status.png'
    plt.savefig(filename, dpi=200, bbox_inches='tight')
    plt.close()
    return filename

# ==================== X 포스팅 ====================
def post_to_x(text, image_path=None):
    client = tweepy.Client(
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_SECRET
    )
    
    if image_path and os.path.exists(image_path):
        auth = tweepy.OAuth1UserHandler(X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET)
        api = tweepy.API(auth)
        media = api.media_upload(image_path)
        media_ids = [media.media_id]
        response = client.create_tweet(text=text, media_ids=media_ids)
    else:
        response = client.create_tweet(text=text)
    
    print("포스팅 완료! ID:", response.data['id'])

# ==================== 메인 ====================
if __name__ == "__main__":
    print("🔋 전력시장 현황 포스팅 시작...")
    
    data = get_power_data()
    if data:
        graph_file = create_graph(data)
        
        now = datetime.now().strftime("%Y년 %m월 %d일 %H시")
        
        tweet = f"""🔋 {now} 한국 전력시장 현황

⚡ 현재수요: {data['demand']:,} MW
🔋 공급능력: {data['supply']:,} MW
📈 예비력: {data['reserve']:,} MW ({data['reserveRate']}%)

#전력시장 #KPX #전력수급 #에너지"""

        post_to_x(tweet, graph_file)
        print("✅ 성공적으로 포스팅했습니다!")
    else:
        print("❌ 데이터 조회 실패")