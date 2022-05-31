/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateGroup } from '../models/CreateGroup';
import type { Group } from '../models/Group';
import type { GroupSearchResponse } from '../models/GroupSearchResponse';
import type { SearchOrder } from '../models/SearchOrder';
import type { UpdateGroup } from '../models/UpdateGroup';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class GroupsService {

    /**
     * Get Groups
     * Get a list of groups filtered by query.
     * @param name
     * @param page
     * @param perPage
     * @param sort
     * @param order
     * @param requestBody
     * @returns GroupSearchResponse Successful Response
     * @throws ApiError
     */
    public static getGroups(
        name?: string,
        page?: number,
        perPage?: number,
        sort?: string,
        order?: SearchOrder,
        requestBody?: Array<number>,
    ): CancelablePromise<GroupSearchResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/groups',
            query: {
                'name': name,
                'page': page,
                'per_page': perPage,
                'sort': sort,
                'order': order,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                401: `Unauthorized`,
                403: `Forbidden`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Create Group
     * Create a new group.
     * @param requestBody
     * @returns Group Successful Response
     * @throws ApiError
     */
    public static createGroup(
        requestBody: CreateGroup,
    ): CancelablePromise<Group> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/groups',
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
     * Get Group
     * Get a group by id.
     * @param groupId
     * @returns Group Successful Response
     * @throws ApiError
     */
    public static getGroup(
        groupId: number,
    ): CancelablePromise<Group> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/groups/{group_id}',
            path: {
                'group_id': groupId,
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
     * Update Group
     * Update a group by id.
     * @param groupId
     * @param requestBody
     * @returns Group Successful Response
     * @throws ApiError
     */
    public static updateGroup(
        groupId: number,
        requestBody: UpdateGroup,
    ): CancelablePromise<Group> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/groups/{group_id}',
            path: {
                'group_id': groupId,
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

    /**
     * Delete Group
     * Delete a group by id.
     * @param groupId
     * @returns void
     * @throws ApiError
     */
    public static deleteGroup(
        groupId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/groups/{group_id}',
            path: {
                'group_id': groupId,
            },
            errors: {
                401: `Unauthorized`,
                403: `Forbidden`,
                404: `Not Found`,
                422: `Validation Error`,
            },
        });
    }

}