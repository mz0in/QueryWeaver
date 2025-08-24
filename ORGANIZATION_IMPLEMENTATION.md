# Organization Management Implementation

This document describes the implementation of organization management functionality for the QueryWeaver text2sql application.

## Overview

The organization management system automatically creates organizations based on email domains and manages user access within those organizations. When users log in for the first time, the system checks their email domain and either creates a new organization or associates them with an existing one.

## Features Implemented

### 1. Automatic Organization Creation
- **Domain-based Organizations**: Organizations are automatically created based on the domain part of user email addresses
- **First User as Admin**: The first user from a domain becomes the organization admin
- **Subsequent Users**: Additional users from the same domain are added as pending members requiring admin approval

### 2. User Roles and Status
- **Admin**: Organization administrators can manage users and approve pending members
- **Member**: Regular organization members with access to organization resources
- **Pending**: Users waiting for admin approval to join the organization

### 3. Admin Management Functions
- **View Members**: Admins can see all organization members and their roles
- **Add Users**: Admins can invite new users by email (must match organization domain)
- **Approve Pending**: Admins can approve users who joined after the organization was created
- **View Pending**: Admins can see all users waiting for approval

## Technical Implementation

### Database Schema (Graph Model)

```cypher
// Nodes
(:User {email, first_name, last_name, created_at})
(:Identity {provider, provider_user_id, email, name, picture, created_at, last_login})
(:Organization {domain, name, created_at, admin_email})

// Relationships
(:Identity)-[:AUTHENTICATES]->(:User)
(:User)-[:BELONGS_TO {is_admin, is_pending, joined_at, invited_by, approved_by}]->(:Organization)
```

### Key Files Created/Modified

#### New Files:
1. **`api/auth/organization_management.py`** - Core organization management functions
2. **`api/routes/organization.py`** - API endpoints for organization management
3. **`api/templates/components/organization_modal.j2`** - Frontend UI component
4. **`test_organization.py`** - Test script and demonstration

#### Modified Files:
1. **`api/auth/user_management.py`** - Updated to integrate with organization management
2. **`api/routes/auth.py`** - Updated login process to handle organizations
3. **`api/app_factory.py`** - Registered new organization blueprint
4. **`api/templates/components/user_profile.j2`** - Added organization management button
5. **`api/templates/chat.j2`** - Included organization modal

### API Endpoints

All endpoints require user authentication via OAuth.

#### GET `/api/organization/status`
Returns the current user's organization status and role.

**Response:**
```json
{
  "has_organization": true,
  "organization": {
    "domain": "example.com",
    "name": "Example",
    "created_at": 1640995200
  },
  "user_role": {
    "is_admin": true,
    "is_pending": false,
    "joined_at": 1640995200
  }
}
```

#### GET `/api/organization/users` (Admin only)
Returns all users in the organization.

#### GET `/api/organization/pending` (Admin only)
Returns all pending users awaiting approval.

#### POST `/api/organization/add-user` (Admin only)
Adds a user to the organization by email.

**Request:**
```json
{
  "email": "newuser@example.com"
}
```

#### POST `/api/organization/approve-user` (Admin only)
Approves a pending user.

**Request:**
```json
{
  "email": "pendinguser@example.com"
}
```

## Usage Flow

### New User Registration Flow

1. **User logs in** with Google/GitHub OAuth
2. **Email domain extracted** from user's email address
3. **Organization check**:
   - If no organization exists for domain → Create new organization, make user admin
   - If organization exists → Add user as pending member
4. **User linked** to organization with appropriate role/status

### Admin Management Flow

1. **Admin accesses** organization management through user profile menu
2. **Views organization status** and member list
3. **Manages pending users** by approving or adding new users by email
4. **Adds new users** by entering their email addresses (domain must match)

## Frontend Integration

### User Interface Components

1. **Organization Button**: Added to user profile dropdown menu
2. **Organization Modal**: Full-featured management interface including:
   - Organization information display
   - Member list with roles
   - Pending user management
   - Add user functionality
   - Admin-only controls with proper permissions

### JavaScript Functions

- `openOrganizationModal()` - Opens the organization management interface
- `loadOrganizationStatus()` - Fetches user's organization information
- `loadOrganizationUsers()` - Fetches organization member list (admin only)
- `loadPendingUsers()` - Fetches pending users (admin only)
- `addUserToOrganization()` - Adds new user by email (admin only)
- `approveUser(email)` - Approves pending user (admin only)

## Security Considerations

### Authentication & Authorization
- All API endpoints require valid OAuth authentication
- Admin-only functions check user role before execution
- Email domain validation ensures users can only be added to their domain's organization

### Data Validation
- Email format validation for all user inputs
- Domain matching validation for new user additions
- Provider validation for OAuth authentication
- Input sanitization for all user-provided data

### Error Handling
- Graceful handling of authentication failures
- Proper error messages for invalid operations
- Fallback behavior when organization management fails

## Testing

### Test Script Usage

```bash
cd /home/guy/workspace/text2sql
python test_organization.py
```

The test script validates:
- Email domain extraction logic
- API endpoint protection (authentication required)
- Error handling for invalid inputs

### Manual Testing Steps

1. **Start the application**:
   ```bash
   python api/index.py
   ```

2. **Set up OAuth credentials** in `.env` file:
   ```
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   GITHUB_CLIENT_ID=your_github_client_id
   GITHUB_CLIENT_SECRET=your_github_client_secret
   ```

3. **Test organization creation**:
   - Log in with user from domain A (e.g., user1@company.com)
   - Verify user becomes admin of new organization
   - Check organization management interface

4. **Test user addition**:
   - Log in with user from same domain (e.g., user2@company.com)
   - Verify user is added as pending
   - Use admin account to approve user

5. **Test admin functions**:
   - Use admin account to add users by email
   - Approve pending users
   - View organization member list

## Configuration Requirements

### Environment Variables
```
FASTAPI_SECRET_KEY=your_secret_key
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
GITHUB_CLIENT_ID=your_github_oauth_client_id
GITHUB_CLIENT_SECRET=your_github_oauth_client_secret
```

### Database Setup
The implementation uses FalkorDB (Redis-based graph database). Ensure the database is running and accessible through the existing `db` extension.

## Future Enhancements

### Potential Improvements
1. **Organization Settings**: Allow admins to configure organization name and settings
2. **Role Management**: Add more granular roles (viewer, editor, admin)
3. **Bulk User Management**: Allow CSV upload for bulk user addition
4. **User Removal**: Add functionality to remove users from organizations
5. **Organization Transfer**: Allow transfer of admin rights
6. **Audit Logging**: Track organization management actions
7. **Email Notifications**: Send emails when users are added/approved
8. **Multi-organization Support**: Allow users to belong to multiple organizations

### Scalability Considerations
1. **Pagination**: Add pagination for large user lists
2. **Search/Filter**: Add search functionality for user lists
3. **Caching**: Implement caching for organization data
4. **Rate Limiting**: Add rate limiting for admin actions

## Troubleshooting

### Common Issues

1. **Organization not created**: Check email domain extraction and database connectivity
2. **User not linked**: Verify OAuth authentication and user creation process
3. **Admin functions not available**: Check user role and organization status
4. **API authentication errors**: Verify OAuth setup and session management

### Debug Steps

1. Check application logs for error messages
2. Verify database connectivity and graph structure
3. Test OAuth authentication flow
4. Validate API endpoint responses
5. Check browser console for JavaScript errors

## Implementation Summary

This implementation successfully provides:

✅ **Automatic organization creation** based on email domains  
✅ **First user as admin** functionality  
✅ **Pending user approval** system  
✅ **Admin-only user management** interface  
✅ **Email-based user addition** with domain validation  
✅ **Secure API endpoints** with proper authentication  
✅ **User-friendly frontend** interface  
✅ **Comprehensive error handling** and validation  
✅ **Integration with existing OAuth** login system  
✅ **Graph database schema** for efficient relationship management  

The system is ready for production use with proper OAuth configuration and provides a solid foundation for future organizational features.
