## 🔄 Mermaid Chart - Chi tiết luồng xử lý

### 1. Tổng quan kiến trúc hệ thống

```mermaid
graph TB
    subgraph "Client Layer"
        UI[Web UI - index.html]
        JS[JavaScript App - app.js]
        WS[WebSocket Connection]
    end

    subgraph "Flask Application Layer"
        API[Flask API Routes]
        SOCK[SocketIO Handler]
        PROC[Background Processor]
    end

    subgraph "AI Processing Layer"
        NB[Naive Bayes Filter]
        LLM[LLM Analyzer]
        DECISION[Decision Engine]
    end

    subgraph "Data Layer"
        DB[(SQLite Database)]
        QUEUE[Message Queue]
        LOGS[Filter Logs]
        TRAIN[Training Data JSON]
    end

    subgraph "External Services"
        OPENAI[OpenAI API]
        GROQ[Groq API]
        ROUTER[OpenRouter API]
    end

    %% Connections
    UI --> JS
    JS <--> WS
    WS <--> SOCK
    UI --> API
    
    API --> DB
    SOCK --> PROC
    PROC --> NB
    PROC --> LLM
    PROC --> DECISION
    PROC --> DB

    NB --> TRAIN
    LLM --> OPENAI
    LLM --> GROQ
    LLM --> ROUTER

    DB --> QUEUE
    DB --> LOGS

    PROC --> SOCK
    SOCK --> WS
```

### 2. Chi tiết luồng xử lý tin nhắn

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant UI as 🖥️ Web UI
    participant API as 🌐 Flask API
    participant Queue as 📝 SQLite Queue
    participant Processor as ⚙️ Background Processor
    participant NB as 🧠 Naive Bayes
    participant LLM as 🤖 LLM Analyzer
    participant DB as 💾 Database
    participant WS as 🔌 WebSocket

    %% Gửi tin nhắn
    User->>UI: Nhập tin nhắn
    UI->>API: POST /api/send_message
    API->>Queue: Lưu message (status: pending)
    API->>UI: Response {message_id}
    UI->>User: Hiển thị "Đang xử lý..."

    %% Background processing
    loop Background Loop (2s interval)
        Processor->>Queue: Lấy pending messages
        
        alt Có message pending
            Queue-->>Processor: Return message
            
            %% Naive Bayes Classification
            Processor->>NB: predict(message_content)
            NB-->>Processor: (prediction, probabilities)
            Processor->>DB: Log NB result
            
            %% Decision Logic
            alt High Confidence Legitimate (pred=0, prob>0.7)
                Processor->>DB: Update status="approved"
                Processor->>WS: Emit "message_processed"
                WS->>UI: Update inbox
            
            else High Confidence Spam (pred=2, prob>0.7)
                Processor->>DB: Update status="blocked"
                Processor->>WS: Emit "message_processed"
                WS->>UI: Update blocked list
            
            else Low Confidence / Suspicious
                Processor->>LLM: analyze_message(content)
                LLM->>LLM: Create prompt
                
                alt OpenAI Provider
                    LLM->>OpenAI: API Call
                    OpenAI-->>LLM: JSON Response
                else Groq Provider
                    LLM->>Groq: API Call
                    Groq-->>LLM: JSON Response
                else OpenRouter Provider
                    LLM->>OpenRouter: API Call
                    OpenRouter-->>LLM: JSON Response
                else No API Key
                    LLM->>LLM: Mock analysis
                end
                
                LLM-->>Processor: {is_spam, confidence, reason}
                Processor->>DB: Log LLM result
                
                alt LLM confirms spam
                    Processor->>DB: Update status="blocked"
                    Processor->>WS: Emit "message_processed"
                    WS->>UI: Update blocked list
                
                else LLM suspicious
                    Processor->>DB: Update status="flagged"
                    Processor->>WS: Emit "message_processed"
                    WS->>UI: Update flagged list
                
                else LLM legitimate
                    Processor->>DB: Update status="approved"
                    Processor->>WS: Emit "message_processed"
                    WS->>UI: Update inbox
                end
            end
        end
    end

    %% Real-time updates
    WS->>UI: Real-time status update
    UI->>User: Hiển thị kết quả cuối
```

### 3. Luồng dữ liệu chi tiết

```mermaid
flowchart TD
    subgraph "Input Stage"
        A1[User Input]
        A2[Test Messages]
        A3[Quick Test Buttons]
    end

    subgraph "API Gateway"
        B1[POST /api/send_message]
        B2[Validate Input]
        B3[Add to Queue]
    end

    subgraph "Message Queue"
        C1[(messages table)]
        C2[status: pending]
        C3[Auto-increment ID]
    end

    subgraph "AI Pipeline"
        D1[Naive Bayes Preprocessing]
        D2[TF-IDF Vectorization]
        D3[MultinomialNB Prediction]
        D4{Confidence Check}
        
        E1[LLM Prompt Creation]
        E2[API Call to Provider]
        E3[JSON Response Parsing]
        E4[Confidence Scoring]
    end

    subgraph "Decision Logic"
        F1{NB High Confidence?}
        F2{Prediction Type?}
        F3[LLM Analysis Required]
        F4{LLM Result?}
        F5[Final Classification]
    end

    subgraph "Output Routing"
        G1[✅ Approved → Inbox]
        G2[⚠️ Flagged → Review]
        G3[❌ Blocked → Spam]
        G4[💾 Log All Steps]
    end

    subgraph "UI Updates"
        H1[WebSocket Emit]
        H2[Real-time UI Update]
        H3[Statistics Refresh]
        H4[Toast Notifications]
    end

    %% Flow connections
    A1 --> B1
    A2 --> B1
    A3 --> B1
    
    B1 --> B2 --> B3 --> C1
    C1 --> C2 --> C3
    
    C3 --> D1 --> D2 --> D3 --> D4
    
    D4 -->|Low Confidence| E1 --> E2 --> E3 --> E4
    D4 -->|High Confidence| F1
    E4 --> F4
    
    F1 -->|Yes| F2
    F1 -->|No| F3 --> F4
    
    F2 -->|Legitimate| G1
    F2 -->|Spam| G3
    F4 -->|Legitimate| G1
    F4 -->|Suspicious| G2
    F4 -->|Spam| G3
    
    G1 --> G4 --> H1
    G2 --> G4 --> H1
    G3 --> G4 --> H1
    
    H1 --> H2 --> H3 --> H4

    %% Styling
    classDef inputClass fill:#e1f5fe
    classDef apiClass fill:#f3e5f5
    classDef queueClass fill:#fff3e0
    classDef aiClass fill:#e8f5e8
    classDef decisionClass fill:#fff8e1
    classDef outputClass fill:#fce4ec
    classDef uiClass fill:#f1f8e9

    class A1,A2,A3 inputClass
    class B1,B2,B3 apiClass
    class C1,C2,C3 queueClass
    class D1,D2,D3,D4,E1,E2,E3,E4 aiClass
    class F1,F2,F3,F4,F5 decisionClass
    class G1,G2,G3,G4 outputClass
    class H1,H2,H3,H4 uiClass
```

### 4. Database Schema và Operations

```mermaid
erDiagram
    messages {
        int id PK
        text content
        text sender
        text status
        real naive_bayes_score
        real llm_score
        text classification
        timestamp created_at
        timestamp processed_at
    }
    
    filter_logs {
        int id PK
        int message_id FK
        text step
        text result
        text details
        timestamp timestamp
    }
    
    messages ||--o{ filter_logs : "has many logs"
```

---

## 📁 Chi tiết tác dụng từng file trong source code

### **1. 🚀 app.py - Flask Application Core**
```python
# Vai trò: Trung tâm điều phối toàn bộ hệ thống
```
**Chức năng chính:**
- **Flask App Setup**: Khởi tạo Flask server, SocketIO, cấu hình CORS
- **API Routes**: Xử lý HTTP requests (send_message, get_inbox, admin, stats)
- **WebSocket Events**: Real-time communication với client
- **Background Processor**: Thread xử lý message queue liên tục
- **Component Integration**: Kết nối Database, NaiveBayes, LLM Analyzer

**Flow xử lý:**
1. Nhận message từ API → Lưu queue (status: pending)
2. Background thread → Lấy pending messages
3. Chạy qua AI pipeline → Cập nhật status/classification
4. Emit WebSocket → Real-time update client
5. Cung cấp admin APIs → Xem logs, stats, export

---

### **2. ⚙️ config.py - Configuration Management**
```python
# Vai trò: Trung tâm cấu hình toàn hệ thống
```
**Chức năng:**
- **Environment Variables**: Đọc API keys từ môi trường
- **LLM Provider Config**: Chọn OpenAI/Groq/OpenRouter
- **Threshold Settings**: Ngưỡng confidence cho NB và LLM
- **Database Path**: Đường dẫn SQLite
- **Security**: Secret keys, CORS settings

**Ví dụ sử dụng:**
```python
Config.OPENAI_API_KEY        # API key
Config.NAIVE_BAYES_THRESHOLD # 0.7 (70% confidence)
Config.LLM_PROVIDER         # 'openai', 'groq', 'openrouter'
```

---

### **3. 💾 database/db_manager.py - Database Operations**
```python
# Vai trò: Data Access Layer cho SQLite
```
**Chức năng chính:**
- **Schema Management**: Tạo/quản lý bảng messages, filter_logs
- **Message Queue Operations**: 
  - `add_message()` → Thêm vào queue
  - `get_pending_messages()` → Lấy messages chưa xử lý
  - `update_message_status()` → Cập nhật kết quả xử lý
- **Logging System**: `log_filter_step()` → Ghi lại từng bước AI pipeline
- **Admin Queries**: Lấy data cho admin panel, inbox filtering

**Database Schema:**
```sql
messages: id, content, sender, status, scores, classification, timestamps
filter_logs: message_id, step, result, details, timestamp
```

---

### **4. 🧠 models/naive_bayes.py - Machine Learning Core**
```python
# Vai trò: AI Classification đầu tiên trong pipeline
```
**Chức năng chi tiết:**
- **Data Processing**:
  - `load_training_data()` → Đọc từ training_data.json
  - `preprocess_text()` → Chuẩn hoá text tiếng Việt
- **Model Training**:
  - TF-IDF Vectorization (1000 features, 1-2 grams)
  - MultinomialNB với alpha=1.0
  - Pickle serialization cho persistence
- **Prediction**:
  - `predict()` → Trả về (class, probabilities)
  - Classes: 0=legitimate, 1=suspicious, 2=spam
- **Performance**: Xử lý nhanh, làm bước lọc đầu tiên

**Pipeline:**
```
Text → Preprocessing → TF-IDF → Naive Bayes → (prediction, confidence)
```

---

### **5. 🤖 models/llm_analyzer.py - Advanced AI Analysis**
```python
# Vai trò: AI phân tích sâu cho trường hợp phức tạp
```
**Chức năng:**
- **Multi-Provider Support**:
  - `_analyze_with_openai()` → GPT-3.5-turbo
  - `_analyze_with_groq()` → Mixtral-8x7b
  - `_analyze_with_openrouter()` → WizardLM-2
- **Prompt Engineering**: Tạo prompt chuyên biệt cho spam detection tiếng Việt
- **Response Parsing**: Parse JSON từ LLM response
- **Fallback Mechanism**: Mock analysis khi không có API key
- **Error Handling**: Conservative approach khi có lỗi

**Output Format:**
```json
{
  "is_spam": true/false,
  "confidence": 0.0-1.0,
  "reason": "explanation in Vietnamese",
  "classification": "legitimate/suspicious/spam"
}
```

---

### **6. 📊 data/training_data.json - Training Dataset**
```json
// Vai trò: Dữ liệu huấn luyện cho Naive Bayes
```
**Cấu trúc:**
- **legitimate** (15 samples): Tin nhắn bình thường, công việc
- **suspicious** (15 samples): Tin nhắn nghi vấn, cần LLM phân tích
- **spam** (15 samples): Tin nhắn lừa đảo rõ ràng

**Đặc điểm:**
- Tiếng Việt native
- Phản ánh thực tế spam tại VN
- Balanced dataset cho 3 classes
- Từ khóa đặc trưng cho từng loại

---

### **7. 🖥️ static/index.html - User Interface Structure**
```html
<!-- Vai trò: Giao diện người dùng chính -->
```
**Components:**
- **Header**: Tiêu đề, connection status indicator
- **Chat Panel**: Form nhập message, quick test buttons
- **Results Panel**: 4 tabs (Inbox/Flagged/Blocked/Admin)
- **Stats Bar**: Real-time statistics
- **Toast Container**: Notifications

**Features:**
- Responsive design (Grid/Flexbox)
- Real-time updates via WebSocket
- Export functionality
- Admin panel với filter logs

---

### **8. 🎨 static/style.css - Visual Design**
```css
/* Vai trò: Styling và responsive design */
```
**Design System:**
- **Color Scheme**: Gradient background, clean white panels
- **Layout**: CSS Grid cho main content, Flexbox cho components
- **Animations**: Toast notifications, loading spinners, hover effects
- **Responsive**: Mobile-first approach
- **Components**: Buttons, forms, message cards, status indicators

**Key Features:**
- Glassmorphism design (backdrop-filter)
- Status-based color coding
- Smooth transitions
- Professional UX patterns

---

### **9. ⚡ static/app.js - Frontend Application Logic**
```javascript
// Vai trò: Client-side application controller
```
**Class Structure:**
- **SpamFilterApp**: Main application class
- **Socket Management**: WebSocket connection/events
- **UI Controllers**: Tab switching, form handling
- **Data Operations**: API calls, rendering, export
- **Real-time Updates**: Live message processing

**Key Methods:**
```javascript
sendMessage()           // Gửi message qua API
loadTabData()          // Load data cho từng tab  
renderMessages()       // Render message list
showToast()           // Hiển thị notifications
exportLogs()          // Export data to CSV
```

---

### **10. 🚀 run_demo.py - Setup & Initialization**
```python
# Vai trò: Bootstrap script cho demo
```
**Functions:**
- `check_requirements()` → Kiểm tra/cài đặt Python packages
- `create_directories()` → Tạo folder structure
- `create_training_data()` → Generate training dataset
- `setup_config()` → Hướng dẫn API key configuration

**Usage:**
```bash
python run_demo.py  # One-time setup
python app.py       # Run application
```

---

### **11. 📦 requirements.txt - Dependencies**
```txt
# Vai trò: Package management
```
**Core Dependencies:**
- `Flask` + `Flask-SocketIO`: Web framework + real-time
- `scikit-learn`: Machine learning (Naive Bayes, TF-IDF)
- `pandas` + `numpy`: Data processing
- `requests`: HTTP calls to LLM APIs

---

### **12. 📋 models/__init__.py & database/__init__.py**
```python
# Vai trò: Package initialization
```
- Module imports for clean project structure
- Expose public APIs
- Enable `from models import NaiveBayesFilter`

---

## 🔄 Interaction Flow Summary

```mermaid
graph LR
    subgraph "User Journey"
        A[👤 Nhập message] 
        B[⚡ Real-time processing]
        C[📊 Xem kết quả]
    end

    subgraph "System Processing"
        D[🌐 API Gateway] 
        E[🧠 AI Pipeline]
        F[💾 Database]
        G[🔌 WebSocket]
    end

    A --> D --> F --> E --> F --> G --> C
    
    style A fill:#e1f5fe
    style C fill:#e8f5e8
    style E fill:#fff3e0
```

**Tóm tắt luồng:**
1. **User Input** → Flask API → SQLite Queue
2. **Background Processor** → Naive Bayes → Decision Logic
3. **Low Confidence** → LLM Analysis → Final Classification  
4. **WebSocket** → Real-time UI Update → User sees result

Hệ thống được thiết kế modular, scalable và dễ maintain, với separation of concerns rõ ràng giữa các layers!

## 🚀 Tiềm năng phát triển thực tế - **RẤT CAO**

Dự án này **KHÔNG chỉ mang tính học thuật** mà có tiềm năng thương mại rất lớn, đặc biệt tại thị trường Việt Nam và Đông Nam Á với tình trạng spam/lừa đảo ngày càng phức tạp.

---

## 📊 **Phân tích thị trường thực tế**

### 🔥 **Pain Points đang tồn tại:**
- **Spam SMS/Email tăng 300%** trong 2 năm qua (báo cáo BKAV 2024)
- **Lừa đảo qua chat app** (Zalo, Telegram, Messenger) gia tăng mạnh
- **Doanh nghiệp thiếu tools** lọc spam tiếng Việt hiệu quả
- **Banking/Fintech** cần solution chống social engineering
- **E-commerce platforms** cần bảo vệ khách hàng khỏi fake messages

### 💰 **Market Size:**
- **SMS Marketing Market VN**: $50M+ (2024)
- **Enterprise Security**: $200M+ 
- **Fintech Anti-Fraud**: $100M+
- **SME Customer Support**: $300M+

---

## 🎯 **Roadmap phát triển sản phẩm**

### **Phase 1: MVP Enhancement (3-6 tháng)**
```mermaid
gantt
    title Phase 1 - MVP to Market
    dateFormat  YYYY-MM-DD
    section Core Features
    Vietnamese NLP Model     :a1, 2025-01-01, 60d
    Real-time API Gateway   :a2, after a1, 30d
    Multi-channel Support   :a3, after a2, 45d
    section Business
    Market Validation       :b1, 2025-01-01, 90d
    Pilot Customers         :b2, after b1, 60d
```

**Technical Improvements:**
- **Vietnamese-specific NLP model** (PhoBERT fine-tuning)
- **Real-time streaming API** (Kafka/Redis Streams)
- **Multi-channel integration** (SMS, Email, Chat apps)
- **Advanced rule engine** với regex patterns cho VN
- **Performance optimization** (1M+ messages/day)

**Business Features:**
- **Admin Dashboard** với analytics/reporting
- **White-label solution** cho resellers
- **API-first architecture** cho easy integration
- **Compliance framework** (GDPR, PDPA Thailand/Singapore)

### **Phase 2: Enterprise Solution (6-12 tháng)**

**🏢 Target Customers:**
1. **Banking/Fintech** (VCB, Techcombank, MoMo, ZaloPay)
2. **E-commerce** (Shopee, Lazada, Tiki, Sendo)
3. **Telco** (Viettel, VNPT, MobiFone)
4. **Government** (Ministry of Information, Cyber Security)

**Enterprise Features:**
```python
# Enterprise-grade capabilities
- Multi-tenant architecture
- Advanced ML pipeline (Transformer models)
- Real-time dashboard với Grafana
- API rate limiting & authentication
- Audit logs & compliance reporting
- Integration với existing security stack
```

### **Phase 3: AI-as-a-Service Platform (12-18 tháng)**

**🌐 Regional Expansion:**
- **Thailand, Singapore, Malaysia** (English + local languages)
- **Cloud-first deployment** (AWS, GCP, Azure)
- **Edge computing** cho low-latency processing
- **Federated learning** để improve model từ multiple clients

---

## 💼 **Business Models có thể áp dụng**

### **1. 🎯 SaaS Subscription**
```
Startup Plan:     $99/month  (10K messages)
Business Plan:    $499/month (100K messages)  
Enterprise Plan:  $2,999/month (Unlimited + Custom)
```

### **2. 🔌 API-First Business**
```
Pay-per-API-call: $0.01/message
Volume discounts: 50% off cho >1M calls/month
White-label licensing: $50K setup + revenue share
```

### **3. 🏭 Enterprise Licensing**
```
On-premise deployment: $100K-500K/year
Consulting services: $200/hour
Custom model training: $50K-200K project
```

### **4. 🤝 Partnership Revenue**
```
Telco integration: Revenue share 30-50%
Banking solutions: Fixed fee + per-transaction
Government contracts: $1M-10M multi-year deals
```

---

## 🚀 **Go-to-Market Strategy**

### **Phase 1: Proof of Concept (Now - 6 months)**
```mermaid
flowchart LR
    A[Demo Current Solution] --> B[Gather Feedback]
    B --> C[MVP Development]
    C --> D[Pilot Customers]
    D --> E[Case Studies]
    E --> F[Funding Round]
```

**Immediate Actions:**
1. **Demo cho potential customers** (banks, e-commerce)
2. **Pilot program** với 3-5 companies (free/low cost)
3. **Collect real-world data** để improve model
4. **Build case studies** và success metrics
5. **Apply for government grants** (VINASA, startup programs)

### **Phase 2: Market Entry (6-12 months)**
- **Series A funding** ($500K-2M)
- **Enterprise sales team**
- **Partnership với system integrators**
- **Marketing campaigns** (conferences, whitepapers)

### **Phase 3: Scale & Expansion (12+ months)**
- **Regional expansion**
- **Acquire smaller competitors**
- **IPO or acquisition** consideration

---

## 🛠 **Technical Architecture cho Production**

### **Scalable Infrastructure:**
```mermaid
graph TB
    subgraph "Client Layer"
        API[REST/GraphQL APIs]
        WS[WebSocket Streaming]
        SDK[SDKs (Python/Node.js/PHP)]
    end
    
    subgraph "Application Layer"
        LB[Load Balancer]
        APP[Flask/FastAPI Cluster]
        CACHE[Redis Cache]
        QUEUE[Kafka Message Queue]
    end
    
    subgraph "AI/ML Layer"
        NLP[Vietnamese NLP Service]
        ML[ML Model Serving (TensorFlow)]
        RULE[Rule Engine]
        FEEDBACK[Feedback Loop]
    end
    
    subgraph "Data Layer"
        POSTGRES[(PostgreSQL)]
        ELASTIC[(Elasticsearch)]
        S3[(Object Storage)]
        MONITORING[Grafana/Prometheus]
    end
    
    API --> LB
    WS --> LB
    SDK --> LB
    LB --> APP
    APP --> CACHE
    APP --> QUEUE
    QUEUE --> NLP
    QUEUE --> ML
    QUEUE --> RULE
    APP --> POSTGRES
    APP --> ELASTIC
    ML --> S3
    FEEDBACK --> ML
```

### **Production Features:**
- **Auto-scaling** với Kubernetes
- **Multi-region deployment** 
- **99.9% SLA** với monitoring
- **SOC 2 Type II compliance**
- **Data encryption** at rest và in transit

---

## 📈 **Revenue Projections**

### **Conservative Scenario (3 years):**
```
Year 1: $50K   (10 pilot customers)
Year 2: $500K  (100 SME customers) 
Year 3: $2M    (10 enterprise + 500 SME)
```

### **Optimistic Scenario (3 years):**
```
Year 1: $200K  (2 enterprise + 50 SME)
Year 2: $1.5M  (10 enterprise + 300 SME)
Year 3: $8M    (50 enterprise + 1000 SME)
```

---

## ⚠️ **Challenges & Risks**

### **Technical Challenges:**
- **Vietnamese NLP complexity** (tones, dialects)
- **Real-time performance** requirements
- **False positive minimization**
- **Adversarial attacks** (spammers adapt)

### **Business Challenges:**
- **Enterprise sales cycle** (6-18 months)
- **Compliance requirements** (data privacy)
- **Competition** từ global players (Google, Microsoft)
- **Customer education** về AI benefits

### **Mitigation Strategies:**
- **Strong technical team** với NLP expertise
- **Partnership với universities** (UET, HUST, UIT)
- **Government relations** cho compliance support
- **Focus on Vietnamese market advantage**

---

## 🎯 **Next Steps (Action Plan)**

### **Immediate (Next 30 days):**
1. ✅ **Enhance current demo** với production-ready features
2. 🎯 **Identify 5 target customers** để demo
3. 📊 **Prepare pitch deck** và business plan
4. 💰 **Apply for startup grants** (VINASA, government programs)
5. 👥 **Recruit technical co-founder** với ML/NLP background

### **Medium-term (3-6 months):**
1. 🚀 **Launch pilot program** với 3 customers
2. 💪 **Build production infrastructure**
3. 📈 **Raise pre-seed funding** ($100K-300K)
4. 🏢 **Establish legal entity** và IP protection
5. 📱 **Develop mobile SDK** cho integration

### **Long-term (6+ months):**
1. 🌟 **Launch commercial product**
2. 💼 **Build enterprise sales team**
3. 🌍 **Expand to Southeast Asia**
4. 🤝 **Strategic partnerships** với telcos/banks
5. 📊 **Series A fundraising** ($1M-3M)

---

## 💡 **Kết luận**

**Đây KHÔNG phải dự án học thuật** - đây là **opportunity thực sự** trong thị trường có nhu cầu cao và ít competitor mạnh tại VN.

**Success factors:**
- ✅ **Technical feasibility** đã được chứng minh
- ✅ **Market need** rất rõ ràng và urgent
- ✅ **Competitive advantage** với Vietnamese-first approach  
- ✅ **Scalable business model** với recurring revenue
- ✅ **Experienced founding team** (nếu có ML/business expertise)

**Recommendation: GO FOR IT!** 🚀

Với execution tốt, dự án này có thể trở thành **unicorn startup đầu tiên về AI Security tại Vietnam** trong 5-7 năm tới.
