/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Account } from '../models/Account';
import type { AccountSearchResponse } from '../models/AccountSearchResponse';
import type { CreateAccount } from '../models/CreateAccount';
import type { IaasType } from '../models/IaasType';
import type { SearchOrder } from '../models/SearchOrder';
import type { UpdateAccount } from '../models/UpdateAccount';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class AccountService {

    /**
     * Get Accounts
     * Get a list of accounts filtered by query.
     * @param name
     * @param iaas
     * @param type
     * @param page
     * @param perPage
     * @param sort
     * @param order
     * @returns AccountSearchResponse Successful Response
     * @throws ApiError
     */
    public static getAccounts(
        name?: string,
        iaas?: string,
        type?: IaasType,
        page?: number,
        perPage?: number,
        sort: string = 'name',
        order?: SearchOrder,
    ): CancelablePromise<AccountSearchResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/accounts',
            query: {
                'name': name,
                'iaas': iaas,
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
     * Create Account
     * Create a new account.
     * @param requestBody
     * @returns Account Successful Response
     * @throws ApiError
     */
    public static createAccount(
        requestBody: CreateAccount,
    ): CancelablePromise<Account> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/accounts',
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
     * Get Account
     * Get an account by id.
     * @param accountId
     * @returns Account Successful Response
     * @throws ApiError
     */
    public static getAccount(
        accountId: number,
    ): CancelablePromise<Account> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/accounts/{account_id}',
            path: {
                'account_id': accountId,
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
     * Delete Account
     * Delete an account.
     * @param accountId
     * @returns void
     * @throws ApiError
     */
    public static deleteAccount(
        accountId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/accounts/{account_id}',
            path: {
                'account_id': accountId,
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
     * Update Account
     * Update an account.
     * @param accountId
     * @param requestBody
     * @returns Account Successful Response
     * @throws ApiError
     */
    public static updateAccount(
        accountId: number,
        requestBody: UpdateAccount,
    ): CancelablePromise<Account> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/accounts/{account_id}',
            path: {
                'account_id': accountId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                401: `Unauthorized`,
                403: `Forbidden`,
                404: `Not Found`,
                422: `Validation Error`,
            },
        });
    }

}