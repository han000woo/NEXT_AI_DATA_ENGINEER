```sql
-- 테이블 초기화 (필요시)
-- DELETE FROM products; 

INSERT INTO products (name, category, description, price, image_url) VALUES 
-- [Electronics]
('기계식 키보드 (청축)', 'Electronics', '타건감이 경쾌한 개발자 필수템입니다. 시끄러움 주의!', 125000, 'https://images.unsplash.com/photo-1595225476474-87563907a212?auto=format&fit=crop&w=500&q=60'),
('노이즈 캔슬링 헤드셋', 'Electronics', '세상과 단절하고 코딩에만 집중하세요.', 280000, 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=500&q=60'),
('버티컬 마우스', 'Electronics', '손목 터널 증후군과 작별하세요. 인체공학적 디자인.', 89000, 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=500&q=60'),
('32인치 4K 모니터', 'Electronics', '코드가 한 눈에 들어오는 광활한 시야. 피벗 기능 지원.', 450000, 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=500&q=60'),

-- [Furniture / Desk]
('인체공학 메쉬 의자', 'Furniture', '개발자의 허리는 소중하니까요. 럼버 서포트 포함.', 350000, 'https://images.unsplash.com/photo-1505843490538-5133c6c7d0e1?auto=format&fit=crop&w=500&q=60'),
('알루미늄 노트북 거치대', 'Furniture', '거북목 방지. 쿨링 효과는 덤입니다.', 42000, 'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?auto=format&fit=crop&w=500&q=60'),
('RGB 게이밍 장패드', 'Accessories', '책상 위를 화려하게. 방수 기능 포함.', 28000, 'https://mblogthumb-phinf.pstatic.net/MjAxOTEyMTNfNyAg/MDAxNTc2MTY0NjgzMjI1.-08ZGcMf1otuUDiZ6GIPG79rwO5F6eswN9LFikEF6yEg.OLsZxEwWMRNhHPfK4G5hUMqtgUTnCpwmA8jnRTXvIlQg.JPEG.limecom79/KakaoTalk_20191213_002239681.jpg?type=w800'),

-- [Fashion]
('개발자 후드티', 'Fashion', '버그 잡을 때 입으면 집중력이 +10 상승합니다.', 45000, 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&w=500&q=60'),
('블루라이트 차단 안경', 'Fashion', '당신의 눈을 보호하세요. 야근 필수템.', 35000, 'https://images.unsplash.com/photo-1577174881658-0f30ed549adc?auto=format&fit=crop&w=500&q=60'),

-- [Goods / Accessories]
('대용량 커피 머그', 'Goods', '코딩은 카페인으로 돌아갑니다. 500ml 용량.', 15000, 'https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=500&q=60'),
('개발자 스티커 팩', 'Goods', '노트북을 힙하게 꾸며보세요.', 5000, 'https://thumbnail.coupangcdn.com/thumbnails/remote/492x492ex/image/vendor_inventory/76f5/a6db769aec4c3602abebeccd0f2b0c8284bed483ec4a853053f5c91defef.jpg'),
('디버깅용 러버덕 (대형)', 'Goods', '코드가 안 풀릴 땐 이 친구에게 설명해보세요. 최고의 리스너.', 12000, 'https://images.unsplash.com/photo-1559715541-5daf8a0296d0?auto=format&fit=crop&w=500&q=60');
 
```