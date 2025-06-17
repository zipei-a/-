-- 创建 Users 表
CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL, -- 存储哈希后的密码
    email VARCHAR(100) NOT NULL UNIQUE,
    real_name VARCHAR(50),
    phone_number VARCHAR(20) UNIQUE,
    address VARCHAR(255),
    registration_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_date DATETIME,
    INDEX idx_username (username), -- 索引，加速登录验证
    INDEX idx_email (email) -- 索引，用于邮箱查找
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户信息表';

-- 创建 Categories 表
CREATE TABLE IF NOT EXISTS Categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    INDEX idx_category_name (name) -- 索引，加速分类名称查找
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='书籍分类表';

-- 创建 Books 表
CREATE TABLE IF NOT EXISTS Books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    seller_id INT NOT NULL,
    category_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(100),
    isbn VARCHAR(20) UNIQUE, -- ISBN通常是唯一的
    publisher VARCHAR(100),
    publication_date DATE,
    price DECIMAL(10, 2) NOT NULL,
    description TEXT,
    condition_desc VARCHAR(255) COMMENT '书籍品相描述',
    status ENUM('available', 'pending', 'sold', 'removed') NOT NULL DEFAULT 'available' COMMENT '书籍状态：可售、待确认、已售、已下架',
    publish_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
    FOREIGN KEY (seller_id) REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_title (title(50)), -- 索引书名前50个字符
    INDEX idx_seller_id (seller_id),
    INDEX idx_category_id (category_id),
    INDEX idx_status (status),
    INDEX idx_publish_date (publish_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='书籍信息表';

-- 创建 Orders 表
CREATE TABLE IF NOT EXISTS Orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    buyer_id INT NOT NULL,
    order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2) NOT NULL,
    status ENUM('pending_payment', 'paid', 'shipped', 'completed', 'cancelled', 'refunded') NOT NULL DEFAULT 'pending_payment' COMMENT '订单状态',
    shipping_address VARCHAR(255),
    contact_phone VARCHAR(20),
    payment_method VARCHAR(50),
    transaction_id VARCHAR(100) UNIQUE COMMENT '支付平台交易号',
    FOREIGN KEY (buyer_id) REFERENCES Users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_buyer_id (buyer_id),
    INDEX idx_order_date (order_date),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单信息表';

-- 创建 Order_Items 表 (订单项，处理一个订单包含多本书籍的情况)
CREATE TABLE IF NOT EXISTS Order_Items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    price_at_purchase DECIMAL(10, 2) NOT NULL COMMENT '购买时的单价',
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE RESTRICT ON UPDATE CASCADE, -- 书籍被删除时，订单项不应自动删除，但应阻止删除有订单项的书籍
    UNIQUE KEY uq_order_book (order_id, book_id) -- 一个订单中同一种书只出现一次
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单项表';

-- 创建 Reviews 表 
CREATE TABLE IF NOT EXISTS Reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL UNIQUE COMMENT '一个订单通常对应一个评价，或针对订单中的商品评价',
    reviewer_id INT NOT NULL COMMENT '评价者用户ID',
   
    reviewed_user_id INT COMMENT '被评价的用户ID (如卖家)',
    rating TINYINT NOT NULL CHECK (rating >= 1 AND rating <= 5) COMMENT '评分1-5星',
    comment TEXT,
    review_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
     --书籍被删除，评价中的书籍ID可设为NULL
    FOREIGN KEY (reviewed_user_id) REFERENCES Users(user_id) ON DELETE SET NULL ON UPDATE CASCADE, -- 用户被删除，评价中的用户ID可设为NULL
    INDEX idx_reviewer_id (reviewer_id),
    INDEX idx_reviewed_user_id (reviewed_user_id),
    INDEX idx_rating (rating)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户评价表';


-- 索引创建
CREATE INDEX idx_books_isbn ON Books (isbn);
CREATE INDEX idx_books_status_publish_date ON Books (status, publish_date DESC);
CREATE INDEX idx_books_price ON Books (price);

-- Orders 表索引
CREATE INDEX idx_orders_status_order_date ON Orders (status, order_date DESC);

-- Order_Items 表索引

-- Reviews 表索引 


-- 示例数据插入
-- 1. 插入用户 (Users)
INSERT INTO Users (username, password_hash, email, real_name, phone_number, address, registration_date)
VALUES 
('zhangsan', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'zhangsan@example.com', '张三', '13800138000', '某大学A栋101', NOW()),
('lisi', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'lisi@example.com', '李四', '13900139000', '某大学B栋202', NOW());

-- 2. 插入书籍分类 (Categories)
INSERT INTO Categories (name, description)
VALUES 
('计算机科学', '计算机编程、算法、数据结构等相关书籍'),
('文学小说', '各类小说、散文、诗歌等'),
('专业教材', '各学科专业课程教材'),
('考研资料', '考研公共课及专业课复习资料');

-- 3. 插入书籍 (Books)
INSERT INTO Books (seller_id, category_id, title, author, isbn, publisher, publication_date, price, description, condition_desc, status, publish_date)
VALUES (1, 1, '深入理解计算机系统', 'Randal E. Bryant', '9787111278337', '机械工业出版社', '2010-01-01', 80.50, '计算机系统经典教材，深入剖析计算机硬件和软件。', '九成新，有少量笔记', 'available', NOW());
INSERT INTO Books (seller_id, category_id, title, author, isbn, publisher, publication_date, price, description, condition_desc, status, publish_date)
VALUES (1, 3, '高等数学（第七版）上册', '同济大学数学系', '9787040406930', '高等教育出版社', '2014-07-01', 35.00, '大学高等数学教材，经典版本。', '八成新，无笔记', 'available', NOW());
INSERT INTO Books (seller_id, category_id, title, author, isbn, publisher, publication_date, price, description, condition_desc, status, publish_date)
VALUES (1, 2, '红楼梦', '曹雪芹', '9787020002207', '人民文学出版社', '1996-12-01', 45.00, '中国古典四大名著之一。', '七成新，有少量划线', 'available', NOW());
INSERT INTO Books (seller_id, category_id, title, author, isbn, publisher, publication_date, price, description, condition_desc, status, publish_date)
VALUES (1, 4, '考研英语词汇', '新东方', '9787560545964', '浙江教育出版社', '2018-01-01', 28.00, '考研英语词汇必备书籍。', '九成新，无笔记', 'available', NOW());
INSERT INTO Books (seller_id, category_id, title, author, isbn, publisher, publication_date, price, description, condition_desc, status, publish_date)
VALUES (1, 1, '算法导论', 'Thomas H. Cormen', '9787111407010', '机械工业出版社', '2013-01-01', 128.00, '算法领域的经典教材。', '八成新，有少量笔记', 'available', NOW());

-- 4. 插入订单 (Orders)
INSERT INTO Orders (buyer_id, order_date, total_amount, status, shipping_address, contact_phone)
VALUES 
(2, NOW(), 115.50, 'pending_payment', '重庆邮电大学明志苑302', '13900139000');

-- 5. 插入订单项 (Order_Items)
INSERT INTO Order_Items (order_id, book_id, quantity, price_at_purchase)
VALUES 
(1, 1, 1, 80.50),
(1, 2, 1, 35.00);

-- 6. 插入评价 (Reviews) 
INSERT INTO Reviews (order_id, reviewer_id, reviewed_user_id, rating, comment, review_date)
VALUES 
(1, 2, 1, 5, '卖家发货很快，书本保护得很好，非常满意！', NOW());


-- 用户权限管理示例 
GRANT SELECT ON secondhand_bookstore_db.Books TO 'app_user'@'%';
FLUSH PRIVILEGES;