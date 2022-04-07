/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateUser } from '../models/CreateUser';
import type { SearchOrder } from '../models/SearchOrder';
import type { UpdateUser } from '../models/UpdateUser';
import type { User } from '../models/User';
import type { UserSearchResponse } from '../models/UserSearchResponse';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class UserService {

    /**
     * Get Users
     * Get a list of users filtered by query.
     * @param username
     * @param firstName
     * @param lastName
     * @param isAdmin
     * @param twofaEnabled
     * @param page
     * @param perPage
     * @param sort
     * @param order
     * @returns UserSearchResponse Successful Response
     * @throws ApiError
     */
    public static getUsers(
        username?: string,
        firstName?: string,
        lastName?: string,
        isAdmin?: boolean,
        twofaEnabled?: boolean,
        page?: number,
        perPage: number = 20,
        sort: string = 'username',
        order?: SearchOrder,
    ): CancelablePromise<UserSearchResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users',
            query: {
                'username': username,
                'first_name': firstName,
                'last_name': lastName,
                'is_admin': isAdmin,
                'twofa_enabled': twofaEnabled,
                'page': page,
                'per_page': perPage,
                'sort': sort,
                'order': order,
            },
            errors: {
                401: `Unauthorized`,
                403: `Forbidden`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Create User
     * Create a new user.
     * @param requestBody
     * @returns User Successful Response
     * @throws ApiError
     */
    public static createUser(
        requestBody: CreateUser,
    ): CancelablePromise<User> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/users',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                401: `Unauthorized`,
                403: `Forbidden`,
                409: `Conflict`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get User
     * Get a user by ID.
     * @param userId
     * @returns User Successful Response
     * @throws ApiError
     */
    public static getUser(
        userId: number,
    ): CancelablePromise<User> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/{user_id}',
            path: {
                'user_id': userId,
            },
            errors: {
                401: `Unauthorized`,
                403: `Forbidden`,
                404: `Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete User
     * Delete a user.
     * @param userId
     * @returns void
     * @throws ApiError
     */
    public static deleteUser(
        userId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/users/{user_id}',
            path: {
                'user_id': userId,
            },
            errors: {
                401: `Unauthorized`,
                403: `Forbidden`,
                404: `Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update User
     * Update a user.
     * @param userId
     * @param requestBody
     * @returns User Successful Response
     * @throws ApiError
     */
    public static updateUser(
        userId: number,
        requestBody: UpdateUser,
    ): CancelablePromise<User> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/users/{user_id}',
            path: {
                'user_id': userId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                401: `Unauthorized`,
                403: `Forbidden`,
                404: `Not Found`,
                409: `Conflict`,
                422: `Validation Error`,
            },
        });
    }

}