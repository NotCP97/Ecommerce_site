import Axios from 'axios';
import React, {useEffect, useState} from 'react';
import {domain} from '../../env';
import Product from '../Product/Product';

const HomePage = () => {
    const [products, setProducts] = useState(null);

    useEffect(() => {
        const getData = () => {
            Axios({
                method: 'get',
                url: `${domain}/api/listproducts/`,
            }).then((response) => {
                
                setProducts(response.data);
                
            });
        };
        getData();
    }, []);

    const nextPage = async () => {
        Axios({
            method: 'get',
            url: products?.next,
        }).then((res) => {
            setProducts(res.data);
        });
    };

    const previousPage = async () => {
        Axios({
            method: 'get',
            url: products?.previous,
        }).then((res) => {
            setProducts(res.data);
        });
    };

    return (
        
        <div className="container-fluid">
            <div className="row">
                <div className="col-md-9">
                    <div className="row">
                        {products !== null ? (
                            <>
                            {console.log(products)}
                                {products.map((item, i) => (
                                    <div className="col-12 col-sm-8 col-md-6 col-lg-4" key={i}>
                                        <Product item={item}/>
                                    </div>
                                ))}
                            </>
                        ) : (
                            <>
                                <h1>Loading...</h1>
                            </>
                        )}
                    </div>
                    
                </div>
                <div className="col-md-3 mt-3"/>
            </div>
        </div>
    );
};

export default HomePage;
