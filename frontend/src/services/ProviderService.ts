/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Account } from '../models/Account';
import type { Iaas } from '../models/Iaas';
import type { IaasSearchResponse } from '../models/IaasSearchResponse';
import type { IaasType } from '../models/IaasType';
import type { SearchOrder } from '../models/SearchOrder';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class ProviderService {

    /**
     * Get Providers
     * @param name
     * @param type
     * @param page
     * @param perPage
     * @param sort
     * @param order
     * @returns IaasSearchResponse Successful Response
     * @throws ApiError
     */
    public static getProviders(
        name?: string,
        type?: IaasType,
        page?: number,
        perPage: number = 20,
        sort: string = 'name',
        order?: SearchOrder,
    ): CancelablePromise<IaasSearchResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/providers/',
            query: {
                'name': name,
                'type': type,
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
     * Get Provider
     * @param providerId
     * @returns Iaas Successful Response
     * @throws ApiError
     */
    public static getProvider(
        providerId: number,
    ): CancelablePromise<Iaas> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/providers/{provider_id}',
            path: {
                'provider_id': providerId,
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
     * Get Provider Accounts
     * @param providerId
     * @returns Account Successful Response
     * @throws ApiError
     */
    public static getProviderAccounts(
        providerId: number,
    ): CancelablePromise<Array<Account>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/providers/{provider_id}/accounts',
            path: {
                'provider_id': providerId,
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