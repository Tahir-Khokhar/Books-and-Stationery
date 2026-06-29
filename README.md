# Books and Stationery Management System - TODO

## Plan (high level)
1. Fix current broken code: complete `items/views.py`, add missing imports/base views.
2. Create full data model in `items/models.py`: User roles, Book, StationeryItem, Category, Customer, Order, OrderItem.
3. Update `items/admin.py` to register models and improve admin UX.
4. Implement authentication & role-based authorization:
   - Registration, Login, Logout
   - Password change/reset
   - Role assignment (Admin vs Staff/User)
5. Implement views:
   - Admin dashboard with charts + low stock + recent orders + monthly sales
   - Books CRUD with search/filter/pagination
   - Stationery CRUD with search/filter/pagination
   - Categories CRUD
6. Implement urls routing in `Book_and_Stationery/urls.py` and `items/urls.py`.
7. Add templates (Bootstrap 5) for all pages.
8. Add static assets (base layout, navbar, dashboard JS + Chart.js).
9. Add media handling for cover images & item images.
10. Run migrations + create a superuser; verify flows.

## Progress
- [x] Step 1: Fix broken code
- [x] Step 2: Implement models
- [x] Step 3: Admin registration
- [x] Step 4: Auth & roles
- [x] Step 5: Core views
- [x] Step 6: URL routing
- [x] Step 7: Templates
- [x] Step 8: Static + charts
- [x] Step 9: Media settings
- [x] Step 10: Migrate & test


