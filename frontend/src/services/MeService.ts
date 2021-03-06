/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UpdateMe } from '../models/UpdateMe';
import type { UpdateMeResponse } from '../models/UpdateMeResponse';
import type { User } from '../models/User';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class MeService {

    /**
     * Get Self
     * @returns User Successful Response
     * @throws ApiError
     */
    public static getSelf(): CancelablePromise<User> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/me',
            errors: {
                401: `Unauthorized`,
            },
        });
    }

    /**
     * Update Self
     * Update own user.
     * @param requestBody
     * @returns UpdateMeResponse Successful Response
     * @throws ApiError
     */
    public static updateSelf(
        requestBody: UpdateMe,
    ): CancelablePromise<UpdateMeResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/me',
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

}