# Podcast Research Agent 技术分析报告

## 项目概述

Podcast Research Agent (PodPrep AI) 是一个基于事件驱动架构的AI播客研究助手系统。该项目演示了如何构建一个将数据工程和AI处理与应用层解耦的AI驱动应用程序。系统能够自动化播客研究流程，从多种来源（博客、现有播客等）挖掘和分析内容，生成播客访谈研究简报。

## 项目结构

```
podcast-research-agent/
├── web-application/           # NextJS前端应用
│   ├── pages/
│   │   ├── api/              # API路由
│   │   │   ├── create-research-bundle.js
│   │   │   └── bundles/      # Bundle相关API
│   │   ├── index.js          # 主页面
│   │   ├── create-research-bundle.js
│   │   └── bundle/[id].js    # 动态路由
│   ├── components/           # React组件
│   └── package.json          # 前端依赖配置
├── research-agent/           # AI处理服务
│   ├── pages/api/
│   │   ├── process-urls.js   # URL处理API
│   │   └── generate-research-brief.js
│   ├── util/
│   │   ├── publish-to-topic.js
│   │   └── extract-transcripts-from-podcast.js
│   └── package.json          # AI服务依赖配置
├── confluent-config/
│   └── flink-queries.sql     # Flink SQL查询配置
├── images/                   # 文档图片
└── README.md                 # 项目说明文档
```

## 技术栈

### 前端技术栈
- **Next.js 15.0.2**: React全栈框架
- **React 19.0.0-rc**: 用户界面库
- **Bootstrap 5.3.3**: CSS框架
- **MongoDB**: 应用数据库

### 后端AI处理技术栈
- **Next.js 15.0.2**: 作为API服务器
- **@langchain/community**: LangChain社区版
- **@langchain/core**: LangChain核心库
- **@langchain/openai**: OpenAI集成
- **OpenAI GPT-4/GPT-4o-mini**: 大语言模型
- **OpenAI Whisper**: 音频转录服务
- **text-embedding-ada-002**: 文本嵌入模型

### 数据处理与流媒体
- **Apache Kafka (Confluent Cloud)**: 消息队列和事件流
- **Apache Flink**: 实时流处理
- **MongoDB Atlas**: 数据存储和向量搜索
- **Confluent Schema Registry**: 消息模式管理

### 其他技术组件
- **mp3-cutter**: MP3音频切割
- **xml2js**: XML解析（RSS feeds）
- **axios**: HTTP客户端
- **dotenv**: 环境变量管理

## 项目技术方案详细说明

### 1. 事件驱动架构设计

系统采用完全解耦的事件驱动架构：

#### 1.1 架构分层
- **应用层**: NextJS Web应用（web-application），负责用户交互
- **数据层**: MongoDB存储业务数据
- **事件层**: Kafka/Confluent Cloud处理事件流
- **AI处理层**: NextJS API服务（research-agent），执行AI任务

#### 1.2 微服务分离
- **web-application**: 不了解LLM、Kafka或Flink，专注于用户界面
- **research-agent**: 专门的AI处理API端点，由Confluent调用

### 2. 数据库设计

#### 2.1 MongoDB Collections

**research_bundles集合**:
```javascript
{
  guestName: String,      // 嘉宾姓名
  company: String,        // 公司名称
  topic: String,          // 主题
  urls: Array,            // 研究源URL数组
  context: String,        // 上下文信息
  processed: Boolean,     // 处理状态
  created_date: DateTime, // 创建时间
  researchBriefText: String // 生成的研究简报
}
```

**text_embeddings集合**:
```javascript
{
  bundleId: String,       // 关联的Bundle ID
  text: String,           // 文本块内容
  embedding: Array,       // 向量嵌入
  url: String            // 来源URL
}
```

**mined_questions集合**:
```javascript
{
  bundleId: String,       // 关联的Bundle ID
  url: String,            // 来源URL
  questions: String       // 提取的问题
}
```

#### 2.2 向量搜索索引
使用Atlas Vector Search创建索引：
```json
{
  "fields": [
    {
      "numDimensions": 1536,
      "path": "embedding",
      "similarity": "dotProduct",
      "type": "vector"
    },
    {
      "path": "bundleId",
      "type": "filter"
    }
  ]
}
```

### 3. Kafka Topics与Schema设计

#### 3.1 核心Topics
- `podprep_ai.research_bundles.podpre_ai.research_bundles`: MongoDB source connector输出
- `podprep-text-chunks-1`: 文本块和嵌入数据
- `podprep-full-text-1`: 完整文本内容
- `podprep-mined-questions`: 提取的问题
- `processed-research-bundles-1`: 完成处理的Bundle ID

#### 3.2 Schema Registry
每个Topic都有对应的JSON Schema定义，确保数据一致性和兼容性。

### 4. AI处理流水线

#### 4.1 URL内容处理 (/api/process-urls.js)

**核心功能**:
- 处理多种URL类型（网页、Apple Podcast）
- 使用GPT-4o-mini提取或总结网页内容
- 文本分块（500字符，50字符重叠）
- 生成text-embedding-ada-002嵌入
- 播客音频转录（Whisper API）

**处理流程**:
```javascript
// 1. 接收Kafka消息触发
async function handler(req, res) {
  let body = JSON.parse(req.body);
  for(let message of body) {
    if ("fullDocument" in message) {
      const urls = message.fullDocument.urls;
      const bundleId = JSON.parse(message.fullDocument._id)["$oid"];
      processResearchBundle(bundleId, urls);
    }
  }
}

// 2. 处理每个URL
async function processUrls(bundleId, urls) {
  for(let url of urls) {
    let contentArray;
    if (url.includes('podcasts.apple.com')) {
      contentArray = await processPodcastURL(bundleId, url);
    } else {
      contentArray = await processTextURL(url);
    }

    // 发布完整文本到Topic
    publishToTopic(FULL_TEXT_TOPIC, [{ url, bundleId, content }]);

    // 分块并生成嵌入
    const chunks = await getContentChunks(contentArray);
    publishToTopic(TEXT_CHUNKS_TOPIC, textChunks);
  }
}
```

#### 4.2 播客音频处理

**音频处理流水线**:
1. **URL解析**: 从Apple Podcast URL提取播客ID和标题
2. **RSS获取**: 通过iTunes API获取RSS feed
3. **音频下载**: 下载MP3文件
4. **文件分割**: 大于25MB的文件自动分割
5. **语音转录**: 使用OpenAI Whisper API转录
6. **清理**: 删除临时文件

```javascript
async function processPodcastURL(bundleId, url) {
  const mp3Url = await getMp3DownloadUrl(url);
  if (mp3Url) {
    let transcriptions = await transcribeAudio(mp3Url);
    return transcriptions;
  }
  return [];
}
```

### 5. Flink实时流处理

#### 5.1 AI模型创建
```sql
CREATE MODEL `question_generation`
INPUT (text STRING)
OUTPUT (response STRING)
WITH (
  'openai.connection'='openai-connection',
  'provider'='openai',
  'task'='text_generation',
  'openai.model_version' = 'gpt-3.5-turbo',
  'openai.system_prompt' = 'Extract the most interesting questions asked from the text. Paraphrase the questions and seperate each one by a blank line. Do not number the questions.'
);
```

#### 5.2 问题提取流处理
```sql
INSERT INTO `podprep-mined-questions`
SELECT `key`, `bundleId`, `url`, q.response AS questions
FROM `podprep-full-text-1`,
LATERAL TABLE (ml_predict('question_generation', content)) AS q;
```

#### 5.3 完成状态检测
```sql
INSERT INTO `processed-research-bundles-1`
SELECT '' AS id, pmq.bundleId
FROM (
    SELECT bundleId, COUNT(url) AS url_count_mined
    FROM `podprep-mined-questions`
    GROUP BY bundleId
) AS pmq
JOIN (
    SELECT bundleId, COUNT(url) AS url_count_full
    FROM `podprep-full-text-1`
    GROUP BY bundleId
) AS pft
ON pmq.bundleId = pft.bundleId
WHERE pmq.url_count_mined = pft.url_count_full;
```

### 6. 研究简报生成 (/api/generate-research-brief.js)

#### 6.1 RAG检索增强生成

**搜索查询生成**:
```javascript
async function getSearchString(researchBundle) {
  const systemPrompt = `You are an expert in research for an engineering podcast. Using the
    guest name, company, topic, and context, create the best possible query to search a vector
    database for relevant data mined from blog posts and existing podcasts.`;

  const response = await model.invoke([
    new SystemMessage(systemPrompt),
    new HumanMessage(userPrompt)
  ]);

  return response.content;
}
```

**向量检索**:
```javascript
async function getRelevantChunks(bundleId, researchBundle) {
  const searchString = await getSearchString(researchBundle);
  const searchEmbedding = await embeddings.embedQuery(searchString);

  const agg = [
    {
      "$vectorSearch": {
        "index": "vector_index",
        "filter": { "bundleId": { "$eq": bundleId } },
        "path": "embedding",
        "queryVector": searchEmbedding,
        "numCandidates": 150,
        "limit": 15
      }
    }
  ];

  return await coll.aggregate(agg).toArray();
}
```

#### 6.2 研究简报生成

**GPT-4生成流程**:
1. 获取研究Bundle基本信息
2. 提取所有挖掘的问题
3. 进行向量搜索获取相关内容
4. 使用GPT-4生成HTML格式的研究简报

```javascript
const systemPrompt = `You are a podcast host and expert in AI, databases, and data engineering.
  You are interviewing ${researchBundle.guestName} from the company ${researchBundle.company}
  about ${researchBundle.topic}.

  Using the additional context, research material, and set of potential questions, create a
  podcast research brief that contains relevant background about the guest and topic and a list
  of 15 to 20 interesting questions that will help create a technical and interesting conversation.`;
```

## 项目运行时从输入到输出的详细路径

### 阶段1: 用户输入与初始化
1. **用户操作**: 在Web界面填写研究Bundle表单
   - 输入: 嘉宾姓名、公司、主题、URL列表、上下文
   - 路径: `web-application/pages/create-research-bundle.js`

2. **数据保存**:
   - API调用: `POST /api/create-research-bundle`
   - 路径: `web-application/pages/api/create-research-bundle.js`
   - 操作: 保存到MongoDB `research_bundles`集合

### 阶段2: 事件触发与URL处理
3. **MongoDB Change Stream**:
   - MongoDB Source Connector检测新插入的文档
   - 发布消息到: `podprep_ai.research_bundles.podpre_ai.research_bundles` topic

4. **HTTP Sink Connector触发**:
   - Confluent HTTP Sink Connector消费消息
   - 调用: `research-agent/pages/api/process-urls.js`

5. **URL内容处理**:
   ```
   process-urls.js → processResearchBundle() → processUrls() →
   ├── processTextURL() (网页)
   │   ├── axios.get(url) 获取HTML
   │   ├── 清理HTML标签
   │   └── extractOrSummarizeContent() (GPT-4o-mini)
   └── processPodcastURL() (播客)
       ├── getMp3DownloadUrl() 解析Apple Podcast URL
       ├── processMP3() 下载和分割音频
       └── transcribeAudio() (Whisper API)
   ```

6. **内容分块与嵌入**:
   ```
   getContentChunks() →
   ├── RecursiveCharacterTextSplitter (500字符块，50重叠)
   ├── embeddings.embedQuery() (text-embedding-ada-002)
   └── publishToTopic(TEXT_CHUNKS_TOPIC)
   ```

7. **消息发布**:
   - 完整文本 → `podprep-full-text-1` topic
   - 文本块+嵌入 → `podprep-text-chunks-1` topic

### 阶段3: 实时流处理与问题挖掘
8. **MongoDB Sink连接器**:
   - 消费`podprep-text-chunks-1`消息
   - 写入MongoDB `text_embeddings`集合

9. **Flink问题提取**:
   ```
   podprep-full-text-1 topic →
   Flink ml_predict() →
   question_generation模型 (GPT-3.5-turbo) →
   podprep-mined-questions topic
   ```

10. **处理完成检测**:
    ```
    Flink SQL查询 →
    COUNT(podprep-mined-questions.url) == COUNT(podprep-full-text-1.url) →
    processed-research-bundles-1 topic
    ```

### 阶段4: 研究简报生成
11. **简报生成触发**:
    - HTTP Sink Connector消费`processed-research-bundles-1`
    - 调用: `research-agent/pages/api/generate-research-brief.js`

12. **RAG检索流程**:
    ```
    buildResearchBrief() →
    ├── getBundle() 获取Bundle信息
    ├── getExistingResearchQuestions() 获取挖掘的问题
    ├── getSearchString() 生成搜索查询 (GPT-4)
    ├── embeddings.embedQuery() 查询嵌入
    ├── MongoDB Vector Search 获取相关文本块
    └── GPT-4生成最终研究简报
    ```

13. **结果更新**:
    ```
    updateResearchBundle() →
    更新MongoDB research_bundles文档 →
    ├── researchBriefText: HTML格式简报
    └── processed: true
    ```

### 阶段5: 用户查看结果
14. **前端轮询更新**:
    - 主页每5秒调用`/api/bundles`
    - 检查`processed`状态更新

15. **简报展示**:
    - 用户点击已完成的Bundle
    - 路径: `web-application/pages/bundle/[id].js`
    - 显示HTML格式的研究简报

## 数据流图示

```
用户输入 → MongoDB → Kafka → URL处理 → 分块&嵌入 → MongoDB
    ↓                                           ↓
Web界面 ← 轮询更新 ← 简报生成 ← Flink处理 ← 实时流处理
```

## 核心技术特点

1. **完全解耦架构**: Web应用与AI处理完全分离
2. **事件驱动**: 基于Kafka的异步消息处理
3. **实时流处理**: Flink SQL实现复杂的流处理逻辑
4. **多模态AI**: 文本和音频内容的智能处理
5. **向量搜索**: MongoDB Atlas实现高效的语义检索
6. **可扩展性**: 微服务架构支持水平扩展
7. **容错性**: 基于Kafka的可靠消息传递

这个系统展示了现代AI应用的最佳实践，将传统的三层架构与现代的事件驱动架构和AI技术完美结合。