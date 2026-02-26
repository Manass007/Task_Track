-- ============================================================
-- CMS DB — Full Reset + Schema + Seed Data
-- Usage:
--   psql -U postgres -c "DROP DATABASE IF EXISTS cms_db;"
--   psql -U postgres -c "CREATE DATABASE cms_db;"
--   psql -U postgres -d cms_db -f cms_db_reset_seed.sql
-- ============================================================

-- ── DROP existing objects (safe re-run) ─────────────────────
DROP TABLE  IF EXISTS comment  CASCADE;
DROP TABLE  IF EXISTS post     CASCADE;
DROP TABLE  IF EXISTS category CASCADE;
DROP TABLE  IF EXISTS "user"   CASCADE;
DROP TYPE   IF EXISTS post_status CASCADE;
DROP TYPE   IF EXISTS user_role   CASCADE;

-- ── ENUM types ───────────────────────────────────────────────
CREATE TYPE user_role   AS ENUM ('admin', 'author');
CREATE TYPE post_status AS ENUM ('draft', 'published');

-- ── USER ─────────────────────────────────────────────────────
CREATE TABLE "user" (
    user_id    SERIAL       PRIMARY KEY,
    username   VARCHAR(100) NOT NULL,
    email      VARCHAR(255) NOT NULL UNIQUE,
    password   TEXT         NOT NULL,   -- store bcrypt hash in production
    role       user_role    NOT NULL DEFAULT 'author',
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    created_by INT          REFERENCES "user"(user_id),
    updated_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_by INT          REFERENCES "user"(user_id)
);

-- ── CATEGORY ─────────────────────────────────────────────────
CREATE TABLE category (
    category_id SERIAL       PRIMARY KEY,
    name        VARCHAR(150) NOT NULL UNIQUE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    created_by  INT          REFERENCES "user"(user_id),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_by  INT          REFERENCES "user"(user_id)
);

-- ── POST ─────────────────────────────────────────────────────
CREATE TABLE post (
    post_id      SERIAL       PRIMARY KEY,
    user_id      INT          NOT NULL REFERENCES "user"(user_id),
    category_id  INT          NOT NULL REFERENCES category(category_id),
    title        VARCHAR(255) NOT NULL,
    body         TEXT         NOT NULL,
    status       post_status  NOT NULL DEFAULT 'draft',
    media_url    TEXT,
    published_at TIMESTAMPTZ,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    created_by   INT          REFERENCES "user"(user_id),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_by   INT          REFERENCES "user"(user_id)
);

-- ── COMMENT ──────────────────────────────────────────────────
CREATE TABLE comment (
    comment_id  SERIAL      PRIMARY KEY,
    post_id     INT         NOT NULL REFERENCES post(post_id) ON DELETE CASCADE,
    user_id     INT         NOT NULL REFERENCES "user"(user_id),
    category_id INT         NOT NULL REFERENCES category(category_id),
    body        TEXT        NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by  INT         REFERENCES "user"(user_id),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by  INT         REFERENCES "user"(user_id)
);

-- ── INDEXES ──────────────────────────────────────────────────
CREATE INDEX idx_post_user     ON post(user_id);
CREATE INDEX idx_post_category ON post(category_id);
CREATE INDEX idx_post_status   ON post(status);
CREATE INDEX idx_comment_post  ON comment(post_id);
CREATE INDEX idx_comment_user  ON comment(user_id);

-- ============================================================
-- SEED DATA
-- ============================================================

-- ── USERS (12 rows) ──────────────────────────────────────────
-- Passwords are placeholder bcrypt hashes (replace with real hashes in production)

INSERT INTO "user" (username, email, password, role, created_at) VALUES
  ('alice_admin', 'alice@retailcms.com', 'alice_admin', 'admin',  NOW() - INTERVAL '90 days'),
  ('bob_admin',   'bob@retailcms.com',   'bob_admin',   'admin',  NOW() - INTERVAL '85 days'),
  ('carol_author','carol@retailcms.com', 'carol_author','author', NOW() - INTERVAL '80 days'),
  ('dave_author', 'dave@retailcms.com',  'dave_author', 'author', NOW() - INTERVAL '75 days'),
  ('eve_author',  'eve@retailcms.com',   'eve_author',  'author', NOW() - INTERVAL '70 days'),
  ('frank_author','frank@retailcms.com', 'frank_author','author', NOW() - INTERVAL '65 days'),
  ('grace_author','grace@retailcms.com', 'grace_author','author', NOW() - INTERVAL '60 days'),
  ('henry_author','henry@retailcms.com', 'henry_author','author', NOW() - INTERVAL '55 days'),
  ('irene_author','irene@retailcms.com', 'irene_author','author', NOW() - INTERVAL '50 days'),
  ('jack_author', 'jack@retailcms.com',  'jack_author', 'author', NOW() - INTERVAL '45 days'),
  ('kate_author', 'kate@retailcms.com',  'kate_author', 'author', NOW() - INTERVAL '40 days'),
  ('liam_author', 'liam_author@retailcms.com', 'liam_author', 'author', NOW() - INTERVAL '35 days');

-- Set created_by / updated_by for users (admin created everyone)
UPDATE "user" SET created_by = 1, updated_by = 1 WHERE user_id > 1;
UPDATE "user" SET created_by = 1, updated_by = 1 WHERE user_id = 1;


-- ── CATEGORIES (12 rows) ─────────────────────────────────────
INSERT INTO category (name, created_at, created_by, updated_at, updated_by) VALUES
  ('New Arrivals',          NOW() - INTERVAL '88 days', 1, NOW() - INTERVAL '88 days', 1),
  ('Sale & Offers',         NOW() - INTERVAL '86 days', 1, NOW() - INTERVAL '86 days', 1),
  ('Style Guide',           NOW() - INTERVAL '84 days', 1, NOW() - INTERVAL '84 days', 1),
  ('Product Reviews',       NOW() - INTERVAL '82 days', 1, NOW() - INTERVAL '82 days', 1),
  ('Behind the Brand',      NOW() - INTERVAL '80 days', 1, NOW() - INTERVAL '80 days', 1),
  ('How-To & Tips',         NOW() - INTERVAL '78 days', 1, NOW() - INTERVAL '78 days', 1),
  ('Customer Stories',      NOW() - INTERVAL '76 days', 1, NOW() - INTERVAL '76 days', 1),
  ('Sustainability',        NOW() - INTERVAL '74 days', 1, NOW() - INTERVAL '74 days', 1),
  ('Tech & Innovation',     NOW() - INTERVAL '72 days', 2, NOW() - INTERVAL '72 days', 2),
  ('Seasonal Collections',  NOW() - INTERVAL '70 days', 2, NOW() - INTERVAL '70 days', 2),
  ('Collaborations',        NOW() - INTERVAL '68 days', 2, NOW() - INTERVAL '68 days', 2),
  ('Events & Launches',     NOW() - INTERVAL '66 days', 2, NOW() - INTERVAL '66 days', 2);


-- ── POSTS (12 rows) ──────────────────────────────────────────
INSERT INTO post (user_id, category_id, title, body, status, media_url, published_at, created_at, created_by, updated_at, updated_by) VALUES

  (3, 1,
   'Spring Collection 2025 Has Arrived',
   'We are thrilled to announce the launch of our Spring 2025 collection. Featuring lightweight fabrics, bold pastels, and versatile silhouettes designed for the modern lifestyle. Shop the full range online and in-store now.',
   'published', 'https://cdn.retailcms.com/media/spring-2025.jpg',
   NOW() - INTERVAL '60 days', NOW() - INTERVAL '61 days', 1, NOW() - INTERVAL '60 days', 3),

  (4, 2,
   'Mega Summer Sale — Up to 50% Off',
   'Summer is the season of savings! Enjoy up to 50% off on selected items across all categories. From casual wear to formal attire, find your perfect look at unbeatable prices. Sale ends July 31st.',
   'published', 'https://cdn.retailcms.com/media/summer-sale.jpg',
   NOW() - INTERVAL '55 days', NOW() - INTERVAL '56 days', 1, NOW() - INTERVAL '55 days', 4),

  (5, 3,
   '10 Ways to Style a White Linen Shirt',
   'A white linen shirt is a wardrobe essential that never goes out of style. In this guide, we explore ten creative ways to style it — from beach-ready casual looks to polished office outfits.',
   'published', 'https://cdn.retailcms.com/media/linen-shirt-style.jpg',
   NOW() - INTERVAL '50 days', NOW() - INTERVAL '51 days', 1, NOW() - INTERVAL '50 days', 5),

  (6, 4,
   'Review: The All-Day Comfort Sneaker',
   'We put our best-selling All-Day Comfort Sneaker to the test — from morning commutes to evening walks. Read our in-depth review covering fit, durability, and sole support.',
   'published', 'https://cdn.retailcms.com/media/sneaker-review.jpg',
   NOW() - INTERVAL '45 days', NOW() - INTERVAL '46 days', 2, NOW() - INTERVAL '45 days', 6),

  (7, 5,
   'Meet Our Founder: A Vision for Conscious Retail',
   'In an exclusive sit-down, our founder shares the story behind the brand — from a small boutique in 2010 to a nationwide name. Discover the values that drive every design decision.',
   'published', 'https://cdn.retailcms.com/media/founder-story.jpg',
   NOW() - INTERVAL '40 days', NOW() - INTERVAL '41 days', 2, NOW() - INTERVAL '40 days', 7),

  (8, 6,
   'How to Care for Your Wool Knitwear',
   'Proper care extends the life of your favourite knits. This guide covers washing, drying, storing, and de-pilling your wool garments so they stay soft and shaped for years.',
   'published', 'https://cdn.retailcms.com/media/wool-care.jpg',
   NOW() - INTERVAL '35 days', NOW() - INTERVAL '36 days', 1, NOW() - INTERVAL '35 days', 8),

  (9, 7,
   'Customer Spotlight: Real People, Real Style',
   'This month we celebrate our community! Seven of our loyal customers share their personal style stories and how our pieces fit into their everyday lives.',
   'published', 'https://cdn.retailcms.com/media/customer-spotlight.jpg',
   NOW() - INTERVAL '30 days', NOW() - INTERVAL '31 days', 1, NOW() - INTERVAL '30 days', 9),

  (10, 8,
   'Our Commitment to Sustainable Packaging',
   'Starting Q3 2025, all our orders will ship in 100% recycled and biodegradable packaging. Learn about the journey behind this change and what it means for our carbon footprint.',
   'published', 'https://cdn.retailcms.com/media/sustainable-packaging.jpg',
   NOW() - INTERVAL '25 days', NOW() - INTERVAL '26 days', 1, NOW() - INTERVAL '25 days', 10),

  (11, 9,
   'Introducing Smart Fit Technology in Our Denim Range',
   'Our new Smart Fit denim uses adaptive stretch fibres that conform to your body shape throughout the day. Discover the technology behind the comfort in our latest range.',
   'published', 'https://cdn.retailcms.com/media/smart-fit-denim.jpg',
   NOW() - INTERVAL '20 days', NOW() - INTERVAL '21 days', 2, NOW() - INTERVAL '20 days', 11),

  (12, 10,
   'Autumn/Winter 2025 Preview: Dark Botanicals',
   'Get a sneak peek at our upcoming AW25 collection. Inspired by the moody beauty of late autumn, the palette features forest greens, burgundy, and slate grey in luxe textures.',
   'published', 'https://cdn.retailcms.com/media/aw25-preview.jpg',
   NOW() - INTERVAL '15 days', NOW() - INTERVAL '16 days', 1, NOW() - INTERVAL '15 days', 12),

  (3, 11,
   'Exclusive Collab Drop: Studio X Retailcms',
   'We have partnered with independent design studio Studio X to create a 12-piece capsule collection. Limited quantities available. Learn about the creative process behind every piece.',
   'draft', 'https://cdn.retailcms.com/media/studio-x-collab.jpg',
   NULL, NOW() - INTERVAL '10 days', 1, NOW() - INTERVAL '10 days', 3),

  (4, 12,
   'Join Us: Pop-Up Store Launch in Manchester',
   'We are bringing the full Spring 2025 experience to Manchester this July. Join us at our pop-up store for live styling sessions, refreshments, and exclusive in-store-only offers.',
   'draft', NULL,
   NULL, NOW() - INTERVAL '5 days', 1, NOW() - INTERVAL '5 days', 4);


-- ── COMMENTS (12 rows) ───────────────────────────────────────
INSERT INTO comment (post_id, user_id, category_id, body, created_at, created_by, updated_at, updated_by) VALUES

  (1, 5,  1,  'Love the new spring arrivals! The pastel tones are exactly what I was looking for this season.',
   NOW() - INTERVAL '59 days', 5, NOW() - INTERVAL '59 days', 5),

  (1, 6,  1,  'Ordered the linen trousers from this collection — they arrived quickly and the quality is fantastic.',
   NOW() - INTERVAL '58 days', 6, NOW() - INTERVAL '58 days', 6),

  (2, 7,  2,  'The sale prices are incredible. Grabbed three items I had on my wishlist for months!',
   NOW() - INTERVAL '54 days', 7, NOW() - INTERVAL '54 days', 7),

  (3, 8,  3,  'Really helpful tips. I never thought to layer a linen shirt under a blazer — trying that look tomorrow.',
   NOW() - INTERVAL '49 days', 8, NOW() - INTERVAL '49 days', 8),

  (4, 9,  4,  'Totally agree with this review. I have been wearing these sneakers for 3 months and they still feel brand new.',
   NOW() - INTERVAL '44 days', 9, NOW() - INTERVAL '44 days', 9),

  (4, 10, 4,  'Would love to see a version with extra arch support. Otherwise, perfect everyday shoe.',
   NOW() - INTERVAL '43 days', 10, NOW() - INTERVAL '43 days', 10),

  (5, 11, 5,  'Such an inspiring story. It is rare to see a brand that stays true to its founding values as it grows.',
   NOW() - INTERVAL '39 days', 11, NOW() - INTERVAL '39 days', 11),

  (6, 12, 6,  'I have been washing my merino wrong for years! This guide saved my favourite jumper. Thank you!',
   NOW() - INTERVAL '34 days', 12, NOW() - INTERVAL '34 days', 12),

  (7, 3,  7,  'I was featured in this post! Such a wonderful experience working with the team. Highly recommend sharing your story.',
   NOW() - INTERVAL '29 days', 3, NOW() - INTERVAL '29 days', 3),

  (8, 4,  8,  'Great initiative on the sustainable packaging. Would also love to see more info on the supplier chain.',
   NOW() - INTERVAL '24 days', 4, NOW() - INTERVAL '24 days', 4),

  (9, 5,  9,  'The Smart Fit denim is a game changer. Wore them on a 10-hour travel day and they were incredibly comfortable.',
   NOW() - INTERVAL '19 days', 5, NOW() - INTERVAL '19 days', 5),

  (10, 6, 10, 'The dark botanical palette is stunning. Already counting down to the AW25 drop!',
   NOW() - INTERVAL '14 days', 6, NOW() - INTERVAL '14 days', 6);


-- ============================================================
-- VERIFY ROW COUNTS
-- ============================================================
DO $$
DECLARE
  u_count  INT; c_count INT; p_count INT; cm_count INT;
BEGIN
  SELECT COUNT(*) INTO u_count  FROM "user";
  SELECT COUNT(*) INTO c_count  FROM category;
  SELECT COUNT(*) INTO p_count  FROM post;
  SELECT COUNT(*) INTO cm_count FROM comment;

  RAISE NOTICE '✅ Seed complete — users: %, categories: %, posts: %, comments: %',
    u_count, c_count, p_count, cm_count;
END $$;